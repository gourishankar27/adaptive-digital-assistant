"""Phase26 failure invariants; local metadata never authorizes application data."""

import json
import os
import subprocess
import sys

import pytest


def test_singleton_releases_on_process_death_and_never_steals_live_lock(tmp_path):
    from ada.host_security import HostError, Singleton

    path = tmp_path / "operation.lock"
    with Singleton(path):
        process = subprocess.run(
            [
                sys.executable,
                "-c",
                "from ada.host_security import Singleton; "
                "from pathlib import Path; import sys; "
                "Singleton(Path(sys.argv[1])).__enter__()",
                str(path),
            ],
            capture_output=True,
            timeout=10,
        )
        assert process.returncode != 0
        with pytest.raises(HostError, match="already_running"):
            with Singleton(path):
                pytest.fail("Live lease was stolen")
    with Singleton(path):
        pass


@pytest.mark.skipif(os.name != "nt", reason="Actual Windows user DPAPI required")
def test_windows_dpapi_roundtrip_authentication_and_independent_recovery(tmp_path):
    from ada.host_security import HostError, protect, unprotect
    from ada.operations import seal, unseal

    secret = b"Public synthetic unattended backup key"
    protected = protect(secret)
    assert secret not in protected
    assert unprotect(protected) == secret
    with pytest.raises(HostError):
        unprotect(protected[:-1] + bytes([protected[-1] ^ 1]))
    portable = seal(secret, "Public independent disaster recovery phrase")
    assert (
        unprotect(protect(unseal(portable, "Public independent disaster recovery phrase")))
        == secret
    )


def test_configuration_refuses_other_identity_profile_and_plaintext_secret(tmp_path):
    from pydantic import ValidationError

    from ada.host_config import HostConfig

    with pytest.raises(ValidationError):
        HostConfig(
            owner_sid="S-1-5-21-1",
            profile=tmp_path.as_posix(),
            repository=tmp_path.as_posix(),
            backup_password="must never be configuration",
        )


def test_retry_budget_stops_crash_loops_and_does_not_restart_for_provider_down():
    from ada.host_supervisor import RetryBudget, health_action

    budget = RetryBudget(limit=3, stable_seconds=60)
    assert [budget.failed(0), budget.failed(1), budget.failed(2), budget.failed(3)] == [
        1,
        2,
        4,
        None,
    ]
    assert budget.failed(100, uptime=61) == 1
    assert health_action({"database": "ready", "provider": "unreachable"}) == "wait_provider"
    assert health_action({"database": "schema_mismatch", "provider": "ready"}) == "stop_schema"
    assert health_action({"database": "unavailable", "provider": "ready"}) == "wait_database"


def test_resources_unknown_are_not_fabricated_and_pressure_defers_discretionary_work():
    from ada.host_health import discretionary_reason

    healthy = {
        "ac_power": True,
        "disk_free_bytes": 5 * 1024**3,
        "thermal_c": None,
        "memory_available_percent": None,
    }
    assert discretionary_reason(healthy) is None
    assert discretionary_reason(healthy | {"ac_power": False}) == "battery"
    assert discretionary_reason(healthy | {"ac_power": None}) == "power_unknown"
    assert discretionary_reason(healthy | {"disk_free_bytes": 0}) == "disk_pressure"
    assert discretionary_reason(healthy | {"thermal_c": 90}) == "thermal_pressure"
    assert discretionary_reason(healthy | {"memory_available_percent": 4}) == "memory_pressure"


def test_backup_pair_rejects_corruption_and_stale_ledger(tmp_path):
    from ada.host_backup import verify_pair
    from ada.operations import RecoveryError, write_artifact

    phrase = "Public synthetic backup verification phrase"
    artifact = write_artifact(tmp_path / "bad.adaenc", b"corrupt archive", phrase)
    ledger = write_artifact(
        tmp_path / "ledger.adaenc", json.dumps({"created_at": 1}).encode(), phrase
    )
    with pytest.raises(RecoveryError):
        verify_pair(artifact, ledger, phrase)


def test_empty_consolidation_poll_never_reserves_foreground_capacity(harness):
    class Capacity:
        def acquire(self, **kwargs):
            pytest.fail("Empty polling took foreground admission")

    service = harness["app"].state.consolidation
    service.capacity = Capacity()
    assert service.run_once() is False


def test_pressure_gate_does_not_claim_or_read_private_jobs(harness):
    service = harness["app"].state.consolidation
    service.discretionary_allowed = lambda: False
    service.sessions = lambda: pytest.fail("Pressure gate read private jobs")
    assert service.run_once() is False


@pytest.mark.skipif(os.name != "nt", reason="Windows SID and protected ACL rehearsal")
def test_protected_config_identity_and_bounded_paths(tmp_path, monkeypatch):
    from ada.host_config import initialize, load_config
    from ada.host_security import HostError, acl

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "selected-profile"))
    path = tmp_path / "selected-profile/ADA/operations/host.json"
    repository = __import__("pathlib").Path(__file__).resolve().parents[1]
    initialize(path, repository, tmp_path, 18926)
    config, root = load_config(path)
    acl(root)
    assert "\\" not in config.repository and "\\" not in config.backup_directory
    data = json.loads(path.read_text())
    path.write_text(json.dumps(data | {"owner_sid": "S-1-5-21-999999"}))
    with pytest.raises(HostError, match="identity_mismatch"):
        load_config(path)
    path.write_text(json.dumps(data | {"backup_directory": tmp_path.as_posix()}))
    with pytest.raises(HostError, match="profile_mismatch"):
        load_config(path)


@pytest.mark.skipif(os.name != "nt", reason="Real Windowless Task Scheduler plan")
def test_scheduler_plan_is_least_privilege_singleton_and_contains_no_secret(tmp_path, monkeypatch):
    import xml.etree.ElementTree as ET

    from ada.host_config import initialize

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "profile"))
    repository = __import__("pathlib").Path(__file__).resolve().parents[1]
    path = tmp_path / "profile/ADA/operations/host.json"
    initialize(path, repository, tmp_path)
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-File",
            str(repository / "scripts/install-host-operations.ps1"),
            "-Config",
            str(path),
        ],
        capture_output=True,
        timeout=40,
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
    for name in ("Supervisor", "Backup"):
        xml = (path.parent / (name + ".task.xml")).read_text(encoding="utf-16")
        tree = ET.fromstring(xml)
        assert tree.find(".//t:RunLevel", ns).text == "LeastPrivilege"
        assert tree.find(".//t:LogonType", ns).text == "InteractiveToken"
        assert tree.find(".//t:MultipleInstancesPolicy", ns).text == "IgnoreNew"
        assert "pythonw.exe" in tree.find(".//t:Command", ns).text
        assert "password" not in tree.find(".//t:Arguments", ns).text.lower()
        assert tree.find(".//t:BootTrigger", ns) is None
        assert tree.find(".//t:WakeToRun", ns).text == "false"


def test_parent_liveness_probe_cannot_terminate_another_process():
    from ada.host_supervisor import parent_alive

    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(20)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert parent_alive(process.pid)
        assert process.poll() is None
    finally:
        process.terminate()
        process.wait(timeout=10)
    assert not parent_alive(process.pid)


@pytest.mark.skipif(os.name != "nt", reason="Windows Job Object kernel lifecycle")
def test_owned_job_close_stops_only_assigned_children():
    from ada.host_security import OwnedJob

    neighbor = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"])
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"])
    try:
        with OwnedJob() as job:
            job.assign(child)
            assert child.poll() is None and neighbor.poll() is None
        child.wait(timeout=10)
        assert neighbor.poll() is None
    finally:
        for process in (child, neighbor):
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
