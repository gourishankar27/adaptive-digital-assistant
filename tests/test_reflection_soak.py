"""One-minute isolated native host exercise; no deployment, real accounts or model egress."""

import json
import threading
import time
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from test_recovery import recovery_database  # noqa: F401
from test_reflection import enabled

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.host_health import resources
from ada.models import Claim
from ada.operations import backup, read_artifact, unpack
from ada.providers import FakeProvider


def test_one_minute_idle_report_foreground_and_encrypted_backup_interference(
    recovery_database,  # noqa: F811
    tmp_path,
):
    url, binary, _ = recovery_database
    engine, sessions = connect(url)
    settings = Settings(
        database_url=url,
        provider="fake",
        scheduler_enabled=False,
        consolidation_worker_enabled=False,
    )
    owner, token = create_user(sessions, "Public reflection host exercise")
    app = create_app(settings, FakeProvider(), sessions)
    h = {
        "app": app,
        "settings": settings,
        "sessions": sessions,
        "a_id": owner,
        "a": {"Authorization": "Bearer " + token},
    }
    result = {
        "duration_seconds": 60,
        "synthetic_only": True,
        "model_summary_enabled": False,
        "resource_input": "explicit synthetic safe readings; real host snapshot reported separately",
        "gpu_time": None,
        "provider": "fake",
        "backup_verified": False,
    }
    failures = []

    def encrypted_backup():
        try:
            receipt = backup(
                url, binary, tmp_path, "Public synthetic isolated host passphrase", settings
            )
            manifest, _ = unpack(
                read_artifact(receipt["artifact"], "Public synthetic isolated host passphrase")
            )
            result["backup_verified"] = manifest["head"] == "0022" and len(manifest["tables"]) == 77
        except Exception as exc:
            failures.append(type(exc).__name__)

    worker = None
    try:
        with TestClient(app) as client:
            h["client"] = client
            service, clock, scope, _, _ = enabled(h)
            p = client.post("/v1/personalities", headers=h["a"], json={}).json()
            c = client.post(
                "/v1/conversations", headers=h["a"], json={"personality_id": p["id"]}
            ).json()

            def foreground():
                start = time.monotonic()
                response = client.post(
                    f"/v1/conversations/{c['id']}/messages",
                    headers=h["a"],
                    json={
                        "request_id": str(uuid4()),
                        "content": "Public synthetic foreground latency sample.",
                    },
                )
                assert response.status_code == 200
                return (time.monotonic() - start) * 1000

            baseline = [foreground() for _ in range(5)]
            clock[0] += 901000
            began = time.monotonic()
            samples = []
            iterations = 0
            while time.monotonic() - began < 60:
                if iterations == 3:
                    worker = threading.Thread(target=encrypted_backup)
                    worker.start()
                clock[0] += 901000
                if service.queue_once():
                    unit = threading.Thread(target=service.run_once)
                    unit.start()
                    samples.append(foreground())
                    unit.join(3)
                    assert not unit.is_alive()
                else:
                    samples.append(foreground())
                iterations += 1
                time.sleep(2)
            if worker:
                worker.join(20)
            assert not failures and result["backup_verified"]
            result["elapsed_seconds"] = round(time.monotonic() - began, 2)
            result["iterations"] = iterations
            result["baseline_median_ms"] = round(sorted(baseline)[len(baseline) // 2], 2)
            result["foreground_p95_ms"] = round(sorted(samples)[int((len(samples) - 1) * 0.95)], 2)
            result["latency_delta_ms"] = round(
                result["foreground_p95_ms"] - result["baseline_median_ms"], 2
            )
            result["artifact_count"] = len(service.artifacts(owner))
            result["job_count"] = len(service.runs(owner))
            assert result["foreground_p95_ms"] < 2000 and result["latency_delta_ms"] < 500
            assert result["job_count"] <= 3
            with sessions() as db:
                result["claims_created"] = db.scalar(select(func.count()).select_from(Claim))
            assert result["claims_created"] == 0
            # Metadata only; no private process/desktop observation.
            result["host_snapshot"] = resources(tmp_path)
            destination = Path(".pytest_cache/phase28/host-soak.json")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    finally:
        if worker:
            worker.join(20)
        engine.dispose()
