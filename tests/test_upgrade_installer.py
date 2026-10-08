import importlib.util
import json
from pathlib import Path, PureWindowsPath

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ada_upgrade", ROOT / "scripts/apply_upgrade.py")
upgrade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upgrade)


def files(tmp_path):
    bundle, project = tmp_path / "bundle", tmp_path / "project"
    for root in (bundle, project):
        (root / "migrations/versions").mkdir(parents=True)
        (root / "migrations/versions/0001_phase_0_users_personalities_.py").write_text("baseline\n")
        (root / "migrations/versions/0002_scoped_evidence_and_claims.py").write_text("phase1\n")
    old = project / "README.md"
    old.write_bytes(b"Phase 1\r\n")
    (bundle / "README.md").write_text("Phase 2\n")
    (bundle / "new.py").write_text("new module\n")
    manifest = {
        "from_version": "0.1.0",
        "to_version": "0.2.0",
        "baseline_migrations": {
            path.relative_to(project).as_posix(): upgrade.file_hash(path)
            for path in (project / "migrations/versions").glob("*.py")
        },
        "files": [
            {
                "path": "README.md",
                "old_hash": upgrade.file_hash(old),
                "new_hash": upgrade.file_hash(bundle / "README.md"),
            },
            {"path": "new.py", "old_hash": None, "new_hash": upgrade.file_hash(bundle / "new.py")},
        ],
    }
    (bundle / "upgrade-manifest.json").write_text(json.dumps(manifest))
    (project / ".env").write_text("local configuration\n")
    (project / "compose.yaml").write_text("custom port configuration\n")
    return bundle, project


def test_installer_preserves_configuration_backs_up_and_replays(tmp_path):
    bundle, project = files(tmp_path)
    upgrade.apply_upgrade(bundle, project, check_only=True)
    assert (project / "README.md").read_bytes() == b"Phase 1\r\n"
    assert not (project / "new.py").exists()
    upgrade.apply_upgrade(bundle, project)
    assert (project / "README.md").read_text() == "Phase 2\n"
    assert (project / ".env").read_text() == "local configuration\n"
    assert (project / "compose.yaml").read_text() == "custom port configuration\n"
    backups = list((project / "upgrade_backups").glob("*/README.md"))
    assert len(backups) == 1 and backups[0].read_bytes() == b"Phase 1\r\n"
    upgrade.apply_upgrade(bundle, project)
    assert len(list((project / "upgrade_backups").iterdir())) == 1


def test_local_edits_or_corrupt_bundle_stop_all_writes(tmp_path):
    bundle, project = files(tmp_path)
    (project / "README.md").write_text("local edit")
    with pytest.raises(ValueError, match="manual merge"):
        upgrade.apply_upgrade(bundle, project)
    assert not (project / "new.py").exists()
    assert not (project / "upgrade_backups").exists()
    (bundle / "new.py").write_text("changed bundle")
    with pytest.raises(ValueError, match="failed validation"):
        upgrade.apply_upgrade(bundle, project)
    assert (project / "README.md").read_text() == "local edit"


def test_installer_requires_the_original_phase1_migration(tmp_path):
    bundle, project = files(tmp_path)
    (project / "migrations/versions/0002_scoped_evidence_and_claims.py").write_text("modified\n")
    with pytest.raises(ValueError, match="original Phase 1 migrations"):
        upgrade.apply_upgrade(bundle, project)
    assert (project / "README.md").read_text() == "Phase 1\n"
    assert not (project / "new.py").exists()
    assert not (project / "upgrade_backups").exists()


def test_fixture_manifest_handles_windows_relative_paths(tmp_path, monkeypatch):
    # Exercise Windows serialization even when this test is running on Linux.
    native_relative_to = type(tmp_path).relative_to

    def windows_relative_to(path, *args, **kwargs):
        return PureWindowsPath(native_relative_to(path, *args, **kwargs))

    with monkeypatch.context() as patch:
        patch.setattr(type(tmp_path), "relative_to", windows_relative_to)
        bundle, project = files(tmp_path)
    manifest = json.loads((bundle / "upgrade-manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["baseline_migrations"]) == {
        "migrations/versions/0001_phase_0_users_personalities_.py",
        "migrations/versions/0002_scoped_evidence_and_claims.py",
    }
    upgrade.apply_upgrade(bundle, project, check_only=True)
