# Phase 02A — close the Windows installer test failures

Status: fix written in this update; post-fix Windows/PostgreSQL closure pending.
Prerequisite: installed Phase 2. This phase needs no application/schema migration.
Apply STANDARDS and CODEX-WORKFLOW.

## Goal and diagnosis

Make the installer fixture match the archive/manifest format on Windows and
Linux. The real installer expects two exact POSIX migration keys. The fixture
used `str(path.relative_to(project))`, which produces `\\` on Windows. Its keys
therefore failed the initial manifest validation, masking the local-edit and
migration-integrity assertions in two other tests.

## Implemented checkpoint

`tests/test_upgrade_installer.py` uses
`path.relative_to(project).as_posix()` when constructing `baseline_migrations`.
A regression substitutes PureWindowsPath relative results, asserts the two exact
keys and exercises the real check-only installer. This catches the serialization
mistake even on a Linux host. Keep `scripts/apply_upgrade.py` strict.

## Target closure

From the Windows repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_upgrade_installer.py -q
.\.venv\Scripts\python.exe -m ruff check src tests migrations scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations scripts
.\scripts\test-postgres.ps1
```

The installer file should have four passing tests. The full suite must have zero
failures. Expected PostgreSQL-specific skips and the existing test-client warning
are recorded separately; do not describe skipped checks as passed. Record the
actual full counts rather than deriving them from the earlier user's output.

## Scope and exit

No changes to bearer credentials, config, database contents, baseline migrations,
prompt snapshots, runtime chat or package versions. Preserve both original
migration hash checks, corrupt-bundle rejection, dry-run no-write behavior,
backups and idempotent installation tests.

Close the phase only after recording a clean post-fix Windows/PostgreSQL run in
STATUS and WORKLOG. Independent planning work is complete; Phase 03 implementation
starts after that target gate. If another failure appears, investigate its own
trace instead of relaxing the installer to accept a malformed manifest.
