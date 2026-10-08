"""Install reviewed Phase 1 files into an existing Phase 0 checkout."""

import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


def file_hash(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def apply_upgrade(bundle: Path, project: Path, *, check_only=False):
    bundle, project = bundle.resolve(), project.resolve()
    if bundle == project:
        raise ValueError("Extract the upgrade separately from the existing project.")
    manifest = json.loads((bundle / "upgrade-manifest.json").read_text(encoding="utf-8"))
    baseline = project / "migrations/versions/0001_phase_0_users_personalities_.py"
    if not baseline.is_file() or file_hash(baseline) != manifest["phase0_migration_hash"]:
        raise ValueError(
            "Project does not match the original Phase 0 migration. No files were changed."
        )
    pending, conflicts = [], []
    protected = {".env", "compose.yaml", "requirements.lock", "upgrade-manifest.json"}
    for item in manifest["files"]:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts or relative.parts[0].startswith("."):
            raise ValueError("Invalid path in upgrade manifest")
        if relative.as_posix() in protected:
            raise ValueError("Manifest attempts to replace protected configuration")
        source, target = bundle / relative, project / relative
        if not source.resolve().is_relative_to(bundle) or not target.resolve().is_relative_to(
            project
        ):
            raise ValueError(f"Path escapes its project: {relative}")
        if not source.is_file() or file_hash(source) != item["new_hash"]:
            raise ValueError(f"Upgrade file failed validation: {relative}")
        if target.exists():
            if not target.is_file():
                conflicts.append(str(relative))
                continue
            current = file_hash(target)
            if current == item["new_hash"]:
                continue
            if item["old_hash"] is None or current != item["old_hash"]:
                conflicts.append(str(relative))
                continue
        elif item["old_hash"] is not None:
            conflicts.append(str(relative))
            continue
        pending.append((source, target, relative))
    if conflicts:
        raise ValueError(
            "Local changes need a manual merge before upgrade: " + ", ".join(conflicts)
        )
    if check_only:
        print(f"Preflight passed: {len(pending)} files would be updated.")
        return
    if not pending:
        print("Phase 1 source files are already installed.")
        return
    backup = (
        project / "upgrade_backups" / ("phase1-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ"))
    )
    backup.mkdir(parents=True)
    # Back up all existing destinations before any overwrite. Partially copied
    # upgrades are retryable because either old or new file hashes are accepted.
    for _, target, relative in pending:
        if target.is_file():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
    shutil.copy2(bundle / "upgrade-manifest.json", backup / "upgrade-manifest.json")
    for source, target, _ in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    print(f"Installed {len(pending)} files. Original files are in {backup}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        apply_upgrade(Path(__file__).resolve().parents[1], args.project, check_only=args.check)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
