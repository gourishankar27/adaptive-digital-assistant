"""Bounded native host failures against disposable PostgreSQL; no machine policies changed."""

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from test_recovery import recovery_database as recovery_database

from ada.config import Settings
from ada.host_config import HostConfig
from ada.host_health import observe
from ada.host_runtime import admission_owner
from ada.host_security import HostError, private_directory, sid
from ada.host_supervisor import supervise

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Native Windows supervised runtime")


@pytest.fixture
def case(recovery_database, tmp_path):
    url, binary, _ = recovery_database
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    root = private_directory(tmp_path / "operations")
    config = HostConfig(
        owner_sid=sid(),
        profile=tmp_path.as_posix(),
        repository=Path.cwd().as_posix(),
        pg_bin=str(binary),
        backup_directory=(tmp_path / "backups").as_posix(),
        port=port,
        poll_seconds=2,
        startup_attempts=1,
        crash_limit=1,
        stable_seconds=30,
    )
    return config, root, Settings(database_url=url, provider="fake")


def test_wrong_schema_stops_before_launch_without_migration(case):
    config, root, settings = case
    engine = create_engine(settings.database_url)
    try:
        with engine.begin() as conn:
            conn.execute(text("UPDATE alembic_version SET version_num='0016'"))
        with pytest.raises(HostError, match="schema_upgrade_required"):
            supervise(
                config,
                root,
                settings,
                root / "host.json",
                launch=lambda *a, **k: pytest.fail("Wrong schema launched API"),
            )
        result = json.loads((root / "supervisor.json").read_bytes())
        assert result["code"] == "schema_upgrade_required" and result["child_pid"] is None
        with engine.connect() as conn:
            assert (
                conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0016"
            )
    finally:
        engine.dispose()


def test_database_down_is_bounded_and_does_not_spawn_or_restart_external_tools(case):
    config, root, settings = case
    url = make_url(settings.database_url).set(port=config.port)
    unavailable = settings.model_copy(
        update={"database_url": url.render_as_string(hide_password=False)}
    )
    with pytest.raises(HostError, match="database_startup_budget_exhausted"):
        supervise(
            config,
            root,
            unavailable,
            root / "host.json",
            launch=lambda *a, **k: pytest.fail("Unavailable database launched a process"),
        )
    assert json.loads((root / "supervisor.json").read_bytes())["state"] == "stopped"


def test_unavailable_provider_does_not_fabricate_model_or_database_failure(case):
    config, root, settings = case
    missing = settings.model_copy(
        update={"provider": "ollama", "ollama_url": f"http://127.0.0.1:{config.port}"}
    )
    result = observe(config, root, missing)
    assert result["database"] == "ready"
    assert result["provider"] == "unreachable"
    assert result["model_residency"]["configured_model_loaded"] is None


def test_kernel_and_pg_gate_reject_duplicates_and_release_without_open_transaction(case):
    config, root, settings = case
    other = private_directory(root / "other")
    with admission_owner(settings, root):
        with pytest.raises(HostError, match="inference_owner_already_running"):
            with admission_owner(settings, other):
                pytest.fail("Duplicate API ownership was granted")
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            assert (
                conn.execute(
                    text(
                        "select count(*) from pg_stat_activity where datname=current_database() and state='idle in transaction'"
                    )
                ).scalar_one()
                == 0
            )
        engine.dispose()
    with admission_owner(settings, other):
        pass


def test_real_child_crash_loop_persists_stop_and_cannot_be_reset_by_new_launch(case):
    config, root, settings = case
    children = []

    def failing_child(*args, **kwargs):
        child = subprocess.Popen(
            [sys.executable, "-c", "raise SystemExit(9)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        children.append(child)
        return child

    with pytest.raises(HostError, match="api_crash_loop_stopped"):
        supervise(config, root, settings, root / "host.json", launch=failing_child)
    assert len(children) == 2 and all(child.poll() is not None for child in children)
    assert (root / "crash-stop.json").is_file()
    with pytest.raises(HostError, match="operator_reset"):
        supervise(
            config,
            root,
            settings,
            root / "host.json",
            launch=lambda *a, **k: pytest.fail("Crash stop was bypassed"),
        )
