"""Windows logon operations. No tasks or power policy are installed by this module."""

import argparse
import getpass
import json
import os
import secrets
import sys
from pathlib import Path

from ada.host_security import HostError, acl, private_directory, protect, timestamp


def emit(value):
    if sys.stdout is not None:
        print(json.dumps(value, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=(
            "init",
            "check-config",
            "check-key",
            "health",
            "enroll-key",
            "recover-key",
            "backup",
            "ledger",
            "verify-backup",
            "restore",
            "supervise",
            "serve",
            "stop",
            "reset-crash-stop",
            "foreground",
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("LOCALAPPDATA", ".")) / "ADA/operations/host.json",
    )
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--pg-bin", type=Path)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--listen", choices=("127.0.0.1", "::1"), default="127.0.0.1")
    parser.add_argument("--recovery-key", type=Path)
    parser.add_argument("--run")
    parser.add_argument("--database")
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--deletion-ledger", type=Path)
    args = parser.parse_args()
    try:
        from ada.config import Settings
        from ada.host_config import initialize, load_config

        if args.action == "init":
            if args.pg_bin is None:
                raise HostError("pg_bin_required")
            initialize(args.config, args.repository, args.pg_bin, args.port)
            emit({"state": "configuration_created", "tasks_installed": False})
            return
        if args.action == "foreground":
            from ada.host_runtime import foreground

            foreground(Settings(), args.listen, args.port)
            return
        config, root = load_config(args.config)
        os.chdir(config.repository)
        if args.action == "check-config":
            emit(
                {
                    "state": "validated",
                    "owner_sid": config.owner_sid,
                    "repository": config.repository,
                    "config": args.config.resolve().as_posix(),
                    "daily_backup_time": config.daily_backup_time,
                }
            )
            return
        if args.action in ("enroll-key", "recover-key"):
            from ada.operations import read_artifact, write_artifact

            if args.recovery_key is None or not args.recovery_key.is_absolute():
                raise HostError("absolute_recovery_key_path_required")
            target = root / "backup-key.dpapi"
            if target.exists():
                raise HostError("backup_key_exists")
            phrase = getpass.getpass("Independent recovery wrapping passphrase (16+ characters): ")
            if len(phrase) < 16:
                raise HostError("recovery_phrase_too_short")
            if args.action == "enroll-key":
                if phrase != getpass.getpass("Repeat recovery wrapping passphrase: "):
                    raise HostError("recovery_phrase_mismatch")
                secret = secrets.token_urlsafe(48).encode("ascii")
                portable = json.dumps(
                    {"format": "ada-host-recovery-key-v1", "key": secret.decode()}
                ).encode()
                write_artifact(args.recovery_key, portable, phrase)
            else:
                portable = json.loads(read_artifact(args.recovery_key, phrase))
                if portable["format"] != "ada-host-recovery-key-v1":
                    raise HostError("unsupported_recovery_key")
                secret = portable["key"].encode("ascii")
            with target.open("xb") as stream:
                stream.write(protect(secret))
            private_directory(config.backup_directory)
            emit({"state": "key_enrolled", "tasks_installed": False})
            return
        settings = Settings()
        if args.action == "check-key":
            from ada.host_backup import key

            key(root)
            emit({"state": "key_available"})
        elif args.action == "health":
            from ada.host_health import observe

            emit(observe(config, root, settings))
        elif args.action == "backup":
            from ada.host_backup import run_backup

            result = run_backup(config, root, settings)
            emit(
                {
                    key: value
                    for key, value in result.items()
                    if key not in ("directory", "artifact", "ledger")
                }
            )
            if result["state"] != "verified":
                raise HostError("backup_deferred")
        elif args.action == "ledger":
            from ada.host_backup import refresh_ledger

            refresh_ledger(config, root, settings)
            emit({"state": "ledger_verified", "verified_at": timestamp()})
        elif args.action == "verify-backup":
            import hashlib

            from ada.host_backup import key, verify_pair

            receipt = json.loads((root / "backup-latest.json").read_bytes())
            destination = Path(config.backup_directory)
            acl(destination)
            if receipt["directory"] != destination.as_posix() or any(
                Path(receipt[name]).name != receipt[name] for name in ("artifact", "ledger")
            ):
                raise HostError("invalid_backup_receipt")
            for name in ("artifact", "ledger"):
                if (
                    hashlib.sha256((destination / receipt[name]).read_bytes()).hexdigest()
                    != receipt[name + "_sha256"]
                ):
                    raise HostError("backup_receipt_integrity_mismatch")
            manifest = verify_pair(
                destination / receipt["artifact"], destination / receipt["ledger"], key(root)
            )
            if manifest["snapshot_at"] != receipt["snapshot_at"]:
                raise HostError("backup_receipt_integrity_mismatch")
            emit(
                {"state": "integrity_verified", "verified_at": timestamp(), "restore_drill": False}
            )
        elif args.action == "restore":
            from ada.host_backup import key, verify_pair
            from ada.operations import restore

            if not args.database or args.artifact is None or args.deletion_ledger is None:
                raise HostError("explicit_restore_target_and_files_required")
            phrase = key(root)
            verify_pair(
                args.artifact,
                args.deletion_ledger,
                phrase,
                max_age_ms=config.backup_fresh_hours * 3600000,
            )
            emit(
                restore(
                    settings.database_url,
                    config.pg_bin,
                    args.database,
                    args.artifact,
                    args.deletion_ledger,
                    phrase,
                )
            )
        elif args.action == "supervise":
            from ada.host_supervisor import supervise

            supervise(config, root, settings, args.config.resolve())
        elif args.action == "serve":
            from ada.host_supervisor import serve

            if (
                args.run is None
                or len(args.run) != 32
                or any(c not in "0123456789abcdef" for c in args.run)
            ):
                raise HostError("supervisor_run_required")
            serve(config, root, settings, args.run)
        elif args.action == "stop":
            from ada.host_supervisor import request_stop

            request_stop(root)
            emit({"state": "stop_requested"})
        elif args.action == "reset-crash-stop":
            from ada.host_security import Singleton

            with Singleton(root / "supervisor.lock"):
                (root / "crash-stop.json").unlink(missing_ok=True)
            emit({"state": "crash_stop_reset"})
    except HostError as exc:
        emit({"state": "failed", "code": str(exc)})
        raise SystemExit(1) from None
    except Exception:
        # Never print exception strings: DB URLs, SQL parameters and key material can be in them.
        emit({"state": "failed", "code": "host_operation_failed"})
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
