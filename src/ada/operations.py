"""Encrypted PostgreSQL recovery artifacts. Never restores into an existing database."""

import argparse
import getpass
import hashlib
import io
import json
import os
import re
import secrets
import subprocess
import threading
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from ada.config import Settings
from ada.inventory import content_tables
from ada.models import now_ms

MAGIC = b"ADA-BACKUP-1\n"
MAX_BYTES = 256 * 1024 * 1024
MEMBERS = {"manifest.json", "database.dump"}


class RecoveryError(Exception):
    """Fixed, non-sensitive operational failure."""


def default_destination():
    root = os.environ.get("LOCALAPPDATA")
    if not root:
        raise RecoveryError("LOCALAPPDATA is required; specify an explicit destination")
    return Path(root) / "ADA" / "backups"


def seal(payload, password):
    if len(payload) > MAX_BYTES or len(password) < 16:
        raise RecoveryError("Artifact too large or passphrase shorter than 16 characters")
    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
    key = Scrypt(salt=salt, length=32, n=32768, r=8, p=1).derive(password.encode())
    header = MAGIC + salt + nonce
    return header + AESGCM(key).encrypt(nonce, payload, header)


def unseal(data, password):
    if not data.startswith(MAGIC) or not len(MAGIC) + 44 <= len(data) <= MAX_BYTES + 128:
        raise RecoveryError("Invalid or oversized encrypted artifact")
    offset = len(MAGIC)
    salt, nonce = data[offset : offset + 16], data[offset + 16 : offset + 28]
    header = data[: offset + 28]
    key = Scrypt(salt=salt, length=32, n=32768, r=8, p=1).derive(password.encode())
    try:
        return AESGCM(key).decrypt(nonce, data[offset + 28 :], header)
    except InvalidTag:
        raise RecoveryError("Artifact authentication failed; no restore performed") from None


def read_artifact(path, password):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 129)
    return unseal(data, password)


def write_artifact(path, payload, password):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: never replace an earlier backup, even on failure.
    encrypted = seal(payload, password)
    with target.open("xb") as stream:
        stream.write(encrypted)
        stream.flush()
        os.fsync(stream.fileno())
    if read_artifact(target, password) != payload:
        raise RecoveryError("Encrypted artifact read-back verification failed")
    return target


def pg_environment(url, database=None):
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or parsed.query:
        raise RecoveryError("Recovery requires PostgreSQL with the default public schema")
    result = {key: value for key, value in os.environ.items() if not key.startswith("PG")}
    result.update(
        PGHOST=parsed.host or "127.0.0.1",
        PGPORT=str(parsed.port or 5432),
        PGUSER=parsed.username or "",
        PGDATABASE=database or parsed.database or "",
        PGCONNECT_TIMEOUT="10",
    )
    if parsed.password:
        result["PGPASSWORD"] = parsed.password
    return result


def pg_tool(binary, arguments, environment, input_bytes=None):
    # No URL/password arguments, stderr, SQL parameters or dump bytes enter diagnostics.
    process = subprocess.Popen(
        [str(binary), *arguments],
        env=environment,
        stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    chunks, failure = [], []

    def collect():
        size = 0
        try:
            while chunk := process.stdout.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_BYTES:
                    failure.append(True)
                    process.kill()
                    break
                chunks.append(chunk)
        except OSError:
            failure.append(True)

    def supply():
        try:
            process.stdin.write(input_bytes)
            process.stdin.close()
        except (BrokenPipeError, OSError):
            failure.append(True)

    reader = threading.Thread(target=collect, daemon=True)
    reader.start()
    writer = None
    if input_bytes is not None:
        writer = threading.Thread(target=supply, daemon=True)
        writer.start()
    try:
        process.wait(timeout=300)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        raise RecoveryError("PostgreSQL recovery tool timed out") from None
    finally:
        reader.join(timeout=5)
        if writer:
            writer.join(timeout=5)
        process.stdout.close()
    if process.returncode or failure or reader.is_alive():
        raise RecoveryError("PostgreSQL recovery tool failed or artifact exceeded size limit")
    return b"".join(chunks)


def check_pg_tools(conn, pg_bin, environment):
    """Conservative rehearsal policy: client tools and server have the same major."""
    major = int(conn.execute(text("SHOW server_version_num")).scalar_one()) // 10000
    for name in ("pg_dump", "pg_restore"):
        binary = Path(pg_bin) / (name + (".exe" if os.name == "nt" else ""))
        version = pg_tool(binary, ["--version"], environment).decode("ascii", errors="replace")
        match = re.search(r"PostgreSQL\) (\d+)(?:\.|\s)", version)
        if not match or int(match[1]) != major:
            raise RecoveryError("PostgreSQL client/server major versions must match")


def database_inventory(conn):
    result = {}
    preparer = conn.dialect.identifier_preparer
    for name in sorted(inspect(conn).get_table_names(schema="public")):
        table = preparer.quote_schema("public") + "." + preparer.quote(name)
        hashes = []
        for row in conn.execute(text(f"SELECT to_jsonb(t)::text FROM {table} t")):
            hashes.append(hashlib.sha256(row[0].encode()).hexdigest())
        result[name] = {
            "rows": len(hashes),
            "sha256": hashlib.sha256("".join(sorted(hashes)).encode()).hexdigest(),
        }
    return result


def deletion_ledger(conn):
    return {
        "format": "ada-deletion-ledger-v1",
        "created_at": now_ms(),
        "owners": [
            dict(row)
            for row in conn.execute(
                text("SELECT id, data_epoch FROM users WHERE data_epoch > 0")
            ).mappings()
        ],
        "requests": [
            dict(row)
            for row in conn.execute(
                text("SELECT owner_id, request_id, job_id, deleted_at FROM deleted_requests")
            ).mappings()
        ],
        "jobs": [
            dict(row)
            for row in conn.execute(
                text("SELECT * FROM deletion_jobs WHERE status='completed'")
            ).mappings()
        ],
    }


def backup(url, pg_bin, destination, password, settings):
    start = time.monotonic()
    engine = create_engine(url)
    try:
        with engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
            with conn.begin():
                conn.execute(text("SET TRANSACTION READ ONLY"))
                head = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                if head != "0015":
                    raise RecoveryError("Backup requires installed schema head 0015")
                from ada.recovery_policy import validate_inventory

                validate_inventory(head, inspect(conn).get_table_names(schema="public"))
                check_pg_tools(conn, pg_bin, pg_environment(url))
                snapshot = conn.execute(text("SELECT pg_export_snapshot()")).scalar_one()
                inventory = database_inventory(conn)
                dump = pg_tool(
                    Path(pg_bin) / "pg_dump.exe" if os.name == "nt" else Path(pg_bin) / "pg_dump",
                    [
                        "--format=custom",
                        "--schema=public",
                        "--no-owner",
                        "--no-acl",
                        "--snapshot=" + snapshot,
                    ],
                    pg_environment(url),
                )
                manifest = {
                    "format": "ada-postgres-backup-v1",
                    "head": head,
                    "snapshot_at": now_ms(),
                    "tables": inventory,
                    "dump_sha256": hashlib.sha256(dump).hexdigest(),
                    "deletion_ledger": deletion_ledger(conn),
                    "configuration": {
                        key: getattr(settings, key)
                        for key in (
                            "provider",
                            "max_parallel",
                            "timeout_seconds",
                            "device_enrollment_enabled",
                            "deletion_worker_enabled",
                            "private_read_limit_per_minute",
                            "private_write_limit_per_minute",
                            "private_max_body_bytes",
                        )
                    },
                    "excluded": [
                        "plaintext tokens",
                        "database passwords",
                        ".env",
                        "TLS/private keys",
                        "client Keystore/cache",
                    ],
                }
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as container:
            container.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
            container.writestr("database.dump", dump)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S") + "-" + secrets.token_hex(4)
        target = write_artifact(
            Path(destination) / (stamp + ".adaenc"), archive.getvalue(), password
        )
        return {
            "artifact": target.as_posix(),
            "seconds": round(time.monotonic() - start, 3),
            "snapshot_at": manifest["snapshot_at"],
            "tables": len(inventory),
        }
    finally:
        engine.dispose()


def unpack(payload):
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            members = archive.infolist()
            if (
                len(members) != 2
                or {item.filename for item in members} != MEMBERS
                or any(
                    item.file_size > MAX_BYTES or item.compress_type != zipfile.ZIP_STORED
                    for item in members
                )
            ):
                raise RecoveryError("Invalid backup member inventory")
            manifest = json.loads(archive.read("manifest.json"))
            dump = archive.read("database.dump")
        if (
            not isinstance(manifest, dict)
            or manifest.get("format") != "ada-postgres-backup-v1"
            or manifest.get("head") != "0015"
            or not isinstance(manifest.get("tables"), dict)
            or type(manifest.get("snapshot_at")) is not int
            or (hashlib.sha256(dump).hexdigest() != manifest.get("dump_sha256"))
        ):
            raise RecoveryError("Backup completeness/integrity check failed")
        return manifest, dump
    except (ValueError, KeyError, zipfile.BadZipFile):
        raise RecoveryError("Invalid backup manifest") from None


def restore(url, pg_bin, target_database, artifact, ledger_path, password):
    start = time.monotonic()
    manifest, dump = unpack(read_artifact(artifact, password))
    from ada.recovery_policy import validate_inventory

    validate_inventory(manifest["head"], manifest["tables"])
    try:
        ledger = json.loads(read_artifact(ledger_path, password))
        if (
            ledger["format"] != "ada-deletion-ledger-v1"
            or ledger["created_at"] < manifest["snapshot_at"]
        ):
            raise RecoveryError("A current post-backup deletion ledger is required")
    except (ValueError, KeyError):
        raise RecoveryError("Invalid deletion ledger") from None
    if not re.fullmatch(r"ada_restore_[a-z0-9_]{1,40}", target_database):
        raise RecoveryError("Target must be a new ada_restore_* database")
    source = make_url(url)
    if target_database == source.database:
        raise RecoveryError("Restore cannot target the configured database")
    pg_environment(url)  # Reject query/credential ambiguity before creating anything.
    admin = create_engine(source.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conn:
            check_pg_tools(conn, pg_bin, pg_environment(url))
            if conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname=:name"), {"name": target_database}
            ).first():
                raise RecoveryError("Restore target already exists; nothing overwritten")
            conn.execute(text(f'CREATE DATABASE "{target_database}" TEMPLATE template0'))
    finally:
        admin.dispose()
    isolated = create_engine(source.set(database=target_database))
    try:
        with isolated.begin() as conn:
            # pg_dump includes CREATE SCHEMA public; this database was just created above.
            conn.execute(text("DROP SCHEMA public"))
    finally:
        isolated.dispose()
    pg_tool(
        Path(pg_bin) / ("pg_restore.exe" if os.name == "nt" else "pg_restore"),
        [
            "--dbname=" + target_database,
            "--single-transaction",
            "--exit-on-error",
            "--no-owner",
            "--no-acl",
        ],
        pg_environment(url, target_database),
        dump,
    )
    engine = create_engine(source.set(database=target_database))
    try:
        with engine.begin() as conn:
            restored_inventory = database_inventory(conn)
            # A backup is not authority to resurrect access, even with revoked-at metadata intact.
            for owner in conn.execute(text("SELECT id FROM users")).scalars().all():
                conn.execute(
                    text("UPDATE users SET token_hash=:digest WHERE id=:owner"),
                    {"digest": hashlib.sha256(secrets.token_bytes(32)).hexdigest(), "owner": owner},
                )
            conn.execute(
                text("UPDATE device_credentials SET revoked_at=COALESCE(revoked_at, :now)"),
                {"now": now_ms()},
            )
        if restored_inventory != manifest["tables"]:
            raise RecoveryError("Restored row hashes/counts differ; credentials quarantined")
        with engine.begin() as conn:
            for entry in ledger["owners"]:
                epoch = conn.execute(
                    text("SELECT data_epoch FROM users WHERE id=:owner"), {"owner": entry["id"]}
                ).scalar_one_or_none()
                if epoch is not None and epoch < entry["data_epoch"]:
                    for table in content_tables():
                        conn.execute(table.delete().where(table.c.owner_id == entry["id"]))
                    conn.execute(
                        text("DELETE FROM deletion_previews WHERE owner_id=:owner"),
                        {"owner": entry["id"]},
                    )
                    conn.execute(
                        text(
                            "UPDATE users SET data_epoch=:epoch, data_revision=data_revision+1, "
                            "deletion_job_id=NULL WHERE id=:owner"
                        ),
                        {"owner": entry["id"], "epoch": entry["data_epoch"]},
                    )
            for entry in ledger["requests"]:
                from sqlalchemy.dialects.postgresql import insert

                from ada.security_models import DeletedRequest

                if conn.execute(
                    text("SELECT 1 FROM users WHERE id=:owner"), {"owner": entry["owner_id"]}
                ).first():
                    conn.execute(insert(DeletedRequest).values(**entry).on_conflict_do_nothing())
            from ada.security_models import DeletionJob

            for entry in ledger["jobs"]:
                exists = conn.execute(
                    text("SELECT 1 FROM users WHERE id=:owner"), {"owner": entry["owner_id"]}
                ).first()
                if exists:
                    conn.execute(
                        DeletionJob.__table__.delete().where(
                            DeletionJob.owner_id == entry["owner_id"], DeletionJob.id == entry["id"]
                        )
                    )
                    conn.execute(DeletionJob.__table__.insert().values(**entry))
    finally:
        engine.dispose()
    return {
        "database": target_database,
        "seconds": round(time.monotonic() - start, 3),
        "snapshot_at": manifest["snapshot_at"],
        "quarantined": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pg-bin", required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    create = sub.add_parser("backup")
    create.add_argument("--destination", type=Path)
    ledger = sub.add_parser("deletion-ledger")
    ledger.add_argument("--output", type=Path, required=True)
    recover = sub.add_parser("restore")
    recover.add_argument("--database", required=True)
    recover.add_argument("--artifact", type=Path, required=True)
    recover.add_argument("--deletion-ledger", type=Path, required=True)
    args = parser.parse_args()
    settings = Settings()
    password = getpass.getpass("Backup passphrase (at least 16 characters): ")
    try:
        if args.action == "backup":
            result = backup(
                settings.database_url,
                args.pg_bin,
                args.destination or default_destination(),
                password,
                settings,
            )
        elif args.action == "deletion-ledger":
            engine = create_engine(settings.database_url)
            try:
                with engine.connect() as conn:
                    value = deletion_ledger(conn)
                target = write_artifact(args.output, json.dumps(value).encode(), password)
                result = {"artifact": target.as_posix()}
            finally:
                engine.dispose()
        else:
            result = restore(
                settings.database_url,
                args.pg_bin,
                args.database,
                args.artifact,
                args.deletion_ledger,
                password,
            )
        print(json.dumps(result, indent=2))
    except Exception:
        # Neither connection URLs nor subprocess/database diagnostics may be printed.
        parser.exit(1, "Recovery operation failed. No existing database was overwritten.\n")


if __name__ == "__main__":
    main()
