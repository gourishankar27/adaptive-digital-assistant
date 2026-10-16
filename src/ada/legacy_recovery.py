"""Encrypted pre-upgrade backup of schema0005; isolated quarantined restoration only."""

import argparse
import getpass
import hashlib
import io
import json
import re
import secrets
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from ada.config import Settings
from ada.models import now_ms
from ada.operations import (
    MAX_BYTES,
    MEMBERS,
    RecoveryError,
    check_pg_tools,
    database_inventory,
    default_destination,
    pg_environment,
    pg_tool,
    read_artifact,
    write_artifact,
)
from ada.recovery_policy import validate_inventory

FORMAT = "ada-postgres-legacy-0005-v1"


def backup_0005(url, pg_bin, destination, password):
    start = time.monotonic()
    engine = create_engine(url)
    try:
        with engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
            with conn.begin():
                conn.execute(text("SET TRANSACTION READ ONLY"))
                if (
                    conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                    != "0005"
                ):
                    raise RecoveryError("Legacy backup requires schema0005; source was not changed")
                validate_inventory("0005", inspect(conn).get_table_names(schema="public"))
                environment = pg_environment(url)
                check_pg_tools(conn, pg_bin, environment)
                snapshot = conn.execute(text("SELECT pg_export_snapshot()")).scalar_one()
                tables = database_inventory(conn)
                dump = pg_tool(
                    Path(pg_bin) / executable("pg_dump"),
                    [
                        "--format=custom",
                        "--schema=public",
                        "--no-owner",
                        "--no-acl",
                        "--snapshot=" + snapshot,
                    ],
                    environment,
                )
                manifest = {
                    "format": FORMAT,
                    "head": "0005",
                    "snapshot_at": now_ms(),
                    "tables": tables,
                    "dump_sha256": hashlib.sha256(dump).hexdigest(),
                }
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as bundle:
            bundle.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
            bundle.writestr("database.dump", dump)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S") + "-" + secrets.token_hex(4)
        artifact = write_artifact(
            Path(destination) / (stamp + ".legacy0005.adaenc"), output.getvalue(), password
        )
        return {
            "artifact": artifact.as_posix(),
            "head": "0005",
            "tables": len(tables),
            "snapshot_at": manifest["snapshot_at"],
            "seconds": round(time.monotonic() - start, 3),
        }
    finally:
        engine.dispose()


def executable(name):
    import os

    return name + (".exe" if os.name == "nt" else "")


def unpack_0005(payload):
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
            members = bundle.infolist()
            if (
                len(members) != 2
                or {m.filename for m in members} != MEMBERS
                or any(
                    m.file_size > MAX_BYTES or m.compress_type != zipfile.ZIP_STORED
                    for m in members
                )
            ):
                raise RecoveryError("Invalid legacy member inventory")
            manifest = json.loads(bundle.read("manifest.json"))
            dump = bundle.read("database.dump")
        if (
            not isinstance(manifest, dict)
            or manifest.get("format") != FORMAT
            or manifest.get("head") != "0005"
            or not isinstance(manifest.get("tables"), dict)
            or type(manifest.get("snapshot_at")) is not int
            or manifest.get("dump_sha256") != hashlib.sha256(dump).hexdigest()
        ):
            raise RecoveryError("Invalid legacy artifact manifest or integrity")
        for value in manifest["tables"].values():
            if (
                not isinstance(value, dict)
                or type(value.get("rows")) is not int
                or value["rows"] < 0
                or not isinstance(value.get("sha256"), str)
                or re.fullmatch("[a-f0-9]{64}", value["sha256"]) is None
            ):
                raise RecoveryError("Invalid legacy row inventory")
        return manifest, dump
    except (ValueError, KeyError, zipfile.BadZipFile):
        raise RecoveryError("Invalid legacy artifact") from None


def restore_0005(url, pg_bin, target_database, artifact, password):
    start = time.monotonic()
    manifest, dump = unpack_0005(read_artifact(artifact, password))
    validate_inventory("0005", manifest["tables"])
    if not re.fullmatch(r"ada_restore_legacy_[a-z0-9_]{1,32}", target_database):
        raise RecoveryError("Legacy restore requires a new isolated ada_restore_legacy_* target")
    parsed = make_url(url)
    if target_database == parsed.database:
        raise RecoveryError("Restore cannot target the configured source")
    environment = pg_environment(url, target_database)
    admin = create_engine(parsed.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conn:
            check_pg_tools(conn, pg_bin, environment)
            if conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname=:name"), {"name": target_database}
            ).first():
                raise RecoveryError("Restore target already exists; no overwrite")
            conn.execute(text(f'CREATE DATABASE "{target_database}" TEMPLATE template0'))
    finally:
        admin.dispose()
    target = create_engine(parsed.set(database=target_database))
    try:
        with target.begin() as conn:
            conn.execute(text("DROP SCHEMA public"))  # Only the newly created isolated DB.
        pg_tool(
            Path(pg_bin) / executable("pg_restore"),
            [
                "--dbname=" + target_database,
                "--single-transaction",
                "--exit-on-error",
                "--no-owner",
                "--no-acl",
            ],
            environment,
            dump,
        )
        with target.begin() as conn:
            restored = database_inventory(conn)
            # Commit quarantine even when subsequent integrity verification refuses recovery.
            for owner in conn.execute(text("SELECT id FROM users")).scalars().all():
                conn.execute(
                    text("UPDATE users SET token_hash=:digest WHERE id=:owner"),
                    {"digest": hashlib.sha256(secrets.token_bytes(32)).hexdigest(), "owner": owner},
                )
        if restored != manifest["tables"]:
            raise RecoveryError("Restored inventory differs; credentials quarantined")
    finally:
        target.dispose()
    return {
        "database": target_database,
        "head": "0005",
        "quarantined": True,
        "reconciliation_required": True,
        "snapshot_at": manifest["snapshot_at"],
        "seconds": round(time.monotonic() - start, 3),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pg-bin", required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    create = sub.add_parser("backup")
    create.add_argument("--destination", type=Path)
    recover = sub.add_parser("restore")
    recover.add_argument("--database", required=True)
    recover.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()
    password = getpass.getpass("Backup passphrase (at least16 characters): ")
    try:
        url = Settings().database_url
        if args.action == "backup":
            result = backup_0005(
                url, args.pg_bin, args.destination or default_destination(), password
            )
        else:
            result = restore_0005(url, args.pg_bin, args.database, args.artifact, password)
        print(json.dumps(result, indent=2))
    except Exception:
        parser.exit(1, "Legacy recovery failed. No existing database was overwritten.\n")


if __name__ == "__main__":
    main()
