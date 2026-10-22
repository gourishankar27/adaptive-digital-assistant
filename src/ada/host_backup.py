"""Narrow unattended backup/ledger operations with protected keys and honest receipts."""

import hashlib
import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text

from ada.host_health import discretionary_reason, resources
from ada.host_security import (
    HostError,
    Singleton,
    acl,
    atomic_json,
    no_redirect,
    timestamp,
    unprotect,
)
from ada.operations import (
    RecoveryError,
    backup,
    deletion_ledger,
    read_artifact,
    unpack,
    write_artifact,
)
from ada.recovery_policy import validate_inventory


def key(root):
    acl(root)
    path = no_redirect(root / "backup-key.dpapi")
    if path.stat().st_size > 16384:
        raise HostError("backup_key_unavailable")
    secret = unprotect(path.read_bytes()).decode("ascii")
    if len(secret) < 32:
        raise HostError("backup_key_unavailable")
    return secret


def current_ledger(settings):
    engine = create_engine(settings.database_url, connect_args={"connect_timeout": 5})
    try:
        with engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
            with conn.begin():
                conn.execute(text("SET TRANSACTION READ ONLY"))
                conn.execute(text("SET statement_timeout=10000"))
                return deletion_ledger(conn)
    finally:
        engine.dispose()


def verify_pair(artifact, ledger, phrase, max_age_ms=None):
    manifest, _ = unpack(read_artifact(artifact, phrase))
    validate_inventory(manifest["head"], manifest["tables"])
    try:
        value = json.loads(read_artifact(ledger, phrase))
        if (
            value["format"] != "ada-deletion-ledger-v1"
            or type(value["created_at"]) is not int
            or value["created_at"] < manifest["snapshot_at"]
            or value["created_at"] > timestamp() + 30000
            or any(not isinstance(value[name], list) for name in ("owners", "requests", "jobs"))
            or (max_age_ms is not None and timestamp() - value["created_at"] > max_age_ms)
        ):
            raise ValueError("stale_ledger")
    except (KeyError, TypeError, ValueError):
        raise RecoveryError("Current consistent deletion ledger required") from None
    return manifest


def refresh_ledger(config, root, settings):
    # This is privacy recovery metadata, not discretionary model work.
    with Singleton(root / "backup.lock"):
        phrase = key(root)
        ledger = current_ledger(settings)
        temporary = root / ("ledger-" + uuid4().hex + ".adaenc")
        try:
            write_artifact(temporary, json.dumps(ledger).encode(), phrase)
            if json.loads(read_artifact(temporary, phrase)) != ledger:
                raise RecoveryError("Ledger verification failed")
            temporary.replace(root / "ledger-current.adaenc")
            atomic_json(
                root / "ledger-latest.json", {"verified_at": timestamp(), "state": "verified"}
            )
        finally:
            temporary.unlink(missing_ok=True)


def run_backup(config, root, settings):
    with Singleton(root / "backup.lock"):
        operation = uuid4().hex
        attempt = {
            "operation": operation,
            "state": "running",
            "started_at": timestamp(),
            "finished_at": None,
            "code": None,
        }
        atomic_json(root / "backup-attempt.json", attempt)
        try:
            destination = no_redirect(config.backup_directory)
            # Enrollment/installation explicitly protects the selected owner's destination.
            acl(destination)
            pause = discretionary_reason(resources(destination))
            if pause:
                attempt.update(state="deferred", code=pause)
                return attempt
            phrase = key(root)
            receipt = backup(settings.database_url, config.pg_bin, destination, phrase, settings)
            artifact = Path(receipt["artifact"])
            ledger = write_artifact(
                destination / (artifact.stem + "-ledger.adaenc"),
                json.dumps(current_ledger(settings)).encode(),
                phrase,
            )
            manifest = verify_pair(artifact, ledger, phrase, max_age_ms=60000)
            result = dict(
                operation=operation,
                state="verified",
                verified_at=timestamp(),
                snapshot_at=manifest["snapshot_at"],
                directory=destination.as_posix(),
                artifact=artifact.name,
                ledger=ledger.name,
                tables=len(manifest["tables"]),
                seconds=receipt["seconds"],
                bytes=artifact.stat().st_size,
                artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                ledger_sha256=hashlib.sha256(ledger.read_bytes()).hexdigest(),
            )
            atomic_json(root / "backup-latest.json", result)
            attempt.update(state="verified")
            return result
        except Exception:
            attempt.update(state="failed", code="backup_not_verified")
            raise HostError("backup_not_verified") from None
        finally:
            attempt["finished_at"] = timestamp()
            atomic_json(root / "backup-attempt.json", attempt)
