"""Real PostgreSQL backup/ledger receipt and failure rehearsal, never application data."""

import json
import os
from pathlib import Path

import pytest
from test_recovery import recovery_database as recovery_database

from ada.config import Settings
from ada.host_backup import key, refresh_ledger, run_backup, verify_pair
from ada.host_config import HostConfig
from ada.host_security import HostError, private_directory, protect, sid
from ada.operations import RecoveryError, read_artifact, restore, write_artifact

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows DPAPI secret provider")


def test_unattended_pair_receipts_restore_and_fail_closed(recovery_database, tmp_path, monkeypatch):
    from ada.auth import create_user
    from ada.db import connect

    url, binary, owned = recovery_database
    root = private_directory(tmp_path / "operations")
    destination = private_directory(tmp_path / "backups")
    phrase = "Public synthetic unattended backup phrase"
    (root / "backup-key.dpapi").write_bytes(protect(phrase.encode()))
    config = HostConfig(
        owner_sid=sid(),
        profile=tmp_path.as_posix(),
        repository=Path.cwd().as_posix(),
        pg_bin=str(binary),
        backup_directory=destination.as_posix(),
    )
    settings = Settings(database_url=url, provider="fake")
    engine, sessions = connect(url)
    create_user(sessions, "Synthetic unattended recovery owner")
    engine.dispose()
    monkeypatch.setattr(
        "ada.host_backup.resources",
        lambda _: dict(
            ac_power=True,
            disk_free_bytes=5 * 1024**3,
            thermal_c=None,
            memory_available_percent=None,
        ),
    )
    result = run_backup(config, root, settings)
    assert result["state"] == "verified" and result["tables"] == 77
    artifact, ledger = destination / result["artifact"], destination / result["ledger"]
    manifest = verify_pair(artifact, ledger, key(root))
    assert manifest["head"] == "0022"
    refresh_ledger(config, root, settings)
    value = json.loads(read_artifact(ledger, phrase))
    stale = write_artifact(
        tmp_path / "stale.adaenc",
        json.dumps(value | {"created_at": manifest["snapshot_at"] - 1}).encode(),
        phrase,
    )
    with pytest.raises(RecoveryError):
        verify_pair(artifact, stale, phrase)
    from uuid import uuid4

    target = "ada_restore_" + uuid4().hex[:12]
    owned.append(target)
    restored = restore(url, binary, target, artifact, root / "ledger-current.adaenc", phrase)
    assert restored["quarantined"] is True
    previous = (root / "backup-latest.json").read_bytes()
    monkeypatch.setattr(
        "ada.host_backup.resources",
        lambda _: dict(
            ac_power=True, disk_free_bytes=0, thermal_c=None, memory_available_percent=None
        ),
    )
    assert run_backup(config, root, settings)["state"] == "deferred"
    assert (root / "backup-latest.json").read_bytes() == previous
    monkeypatch.setattr(
        "ada.host_backup.resources",
        lambda _: dict(
            ac_power=True,
            disk_free_bytes=5 * 1024**3,
            thermal_c=None,
            memory_available_percent=None,
        ),
    )
    (root / "backup-key.dpapi").write_bytes(b"corrupt protected key")
    with pytest.raises(HostError, match="backup_not_verified"):
        run_backup(config, root, settings)
    assert (root / "backup-latest.json").read_bytes() == previous
    assert json.loads((root / "backup-attempt.json").read_bytes())["state"] == "failed"
    assert artifact.is_file()  # No pruning on failure.
