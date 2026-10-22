"""Bounded generation-free local health; unavailable sensors remain null."""

import ctypes
import json
import os
import shutil
import subprocess
from pathlib import Path

import httpx
from sqlalchemy import create_engine, text

from ada.host_security import timestamp
from ada.monitoring import ProviderProbe, _probe_logging, model_key
from ada.providers import FakeProvider, OllamaProvider
from ada.schema import SCHEMA_HEAD


def resources(path):
    result = dict(
        ac_power=None,
        battery_percent=None,
        thermal_c=None,
        gpu_memory_used_mib=None,
        gpu_memory_total_mib=None,
        gpu_utilization=None,
        memory_available_percent=None,
        disk_free_bytes=None,
    )
    try:
        result["disk_free_bytes"] = shutil.disk_usage(Path(path)).free
    except OSError:
        pass
    if os.name == "nt":
        from ctypes import wintypes

        class Power(ctypes.Structure):
            _fields_ = [
                ("ac", wintypes.BYTE),
                ("flag", wintypes.BYTE),
                ("percent", wintypes.BYTE),
                ("reserved", wintypes.BYTE),
                ("life", wintypes.DWORD),
                ("full", wintypes.DWORD),
            ]

        class Memory(ctypes.Structure):
            _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
                (name, ctypes.c_ulonglong)
                for name in (
                    "total",
                    "available",
                    "page_total",
                    "page_available",
                    "virtual",
                    "virtual_available",
                    "extended",
                )
            ]

        power, memory = Power(), Memory()
        memory.length = ctypes.sizeof(memory)
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(power)):
            result["ac_power"] = bool(power.ac) if power.ac in (0, 1) else None
            result["battery_percent"] = power.percent if power.percent <= 100 else None
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)) and memory.total:
            result["memory_available_percent"] = round(100 * memory.available / memory.total, 1)
    binary = shutil.which("nvidia-smi.exe" if os.name == "nt" else "nvidia-smi")
    if binary:
        try:
            output = subprocess.run(
                [
                    binary,
                    "--query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=3,
                check=True,
            ).stdout
            rows = [[float(v.strip()) for v in row.split(",")] for row in output.splitlines()]
            if 0 < len(rows) <= 16 and all(len(row) == 4 for row in rows):
                result.update(
                    gpu_memory_used_mib=sum(row[0] for row in rows),
                    gpu_memory_total_mib=sum(row[1] for row in rows),
                    thermal_c=max(row[2] for row in rows),
                    gpu_utilization=max(row[3] for row in rows),
                )
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    return result


def discretionary_reason(values):
    if values["ac_power"] is False:
        return "battery"
    if values["ac_power"] is None:
        return "power_unknown"
    if values["disk_free_bytes"] is None or values["disk_free_bytes"] < 1024**3:
        return "disk_pressure"
    if values["thermal_c"] is not None and values["thermal_c"] >= 85:
        return "thermal_pressure"
    if values["memory_available_percent"] is not None and values["memory_available_percent"] < 10:
        return "memory_pressure"
    return None


def database_state(settings):
    engine = None
    try:
        engine = create_engine(
            settings.database_url, connect_args={"connect_timeout": 3}, pool_pre_ping=False
        )
        with engine.connect() as conn:
            conn.execute(text("SET statement_timeout=3000"))
            head = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        return "ready" if head == SCHEMA_HEAD else "schema_mismatch"
    except Exception:
        return "unavailable"
    finally:
        if engine is not None:
            engine.dispose()


def api_state(port):
    result = {"api_live": False, "api_ready": False}
    try:
        with httpx.Client(timeout=3, trust_env=False) as client:
            for path, key, expected in (
                ("live", "api_live", "ok"),
                ("ready", "api_ready", "ready"),
            ):
                with client.stream("GET", f"http://127.0.0.1:{port}/health/{path}") as response:
                    body = bytearray()
                    for chunk in response.iter_bytes():
                        body.extend(chunk)
                        if len(body) > 4096:
                            raise ValueError("oversized_health")
                    result[key] = (
                        response.status_code == 200 and json.loads(body).get("status") == expected
                    )
    except (httpx.HTTPError, ValueError):
        pass
    return result


def model_residency(settings):
    """Metadata only: never warms, unloads or selects a different model."""
    if settings.provider != "ollama":
        return {"configured_model_loaded": None, "loaded_models": None}
    _probe_logging.active = True
    try:
        with httpx.Client(
            base_url=settings.ollama_url,
            timeout=3,
            trust_env=False,
            headers={"Accept-Encoding": "identity"},
        ) as client:
            with client.stream("GET", "/api/ps") as response:
                response.raise_for_status()
                body = bytearray()
                began = __import__("time").monotonic()
                for chunk in response.iter_bytes():
                    body.extend(chunk)
                    if len(body) > 256000 or __import__("time").monotonic() - began > 3:
                        raise ValueError("invalid_metadata")
                models = json.loads(body)["models"]
                if not isinstance(models, list) or any(
                    not isinstance(m.get("name"), str) for m in models
                ):
                    raise ValueError("invalid_metadata")
        return {
            "configured_model_loaded": any(
                model_key(m["name"]) == model_key(settings.ollama_model) for m in models
            ),
            "loaded_models": len(models),
        }
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
        return {"configured_model_loaded": None, "loaded_models": None}
    finally:
        _probe_logging.active = False


def backup_state(root, fresh_hours):
    result = {
        "state": "missing",
        "last_verified_at": None,
        "age_seconds": None,
        "last_attempt": None,
        "ledger_verified_at": None,
        "ledger_state": "missing",
    }
    try:
        attempt = json.loads((root / "backup-attempt.json").read_bytes())
        result["last_attempt"] = (
            attempt["state"]
            if attempt["state"] in ("running", "verified", "failed", "deferred")
            else "unknown"
        )
    except (OSError, ValueError, KeyError):
        pass
    try:
        receipt = json.loads((root / "backup-latest.json").read_bytes())
        checked = receipt["verified_at"]
        if receipt["state"] != "verified" or type(checked) is not int:
            raise ValueError("invalid_receipt")
        age = max(0, timestamp() - checked) // 1000
        result.update(
            state="current" if age <= fresh_hours * 3600 else "stale",
            last_verified_at=checked,
            age_seconds=age,
        )
        for key in ("artifact", "ledger"):
            name = receipt[key]
            if Path(name).name != name or not (Path(receipt["directory"]) / name).is_file():
                result["state"] = "artifact_missing"
    except (OSError, ValueError, KeyError, TypeError):
        pass
    try:
        ledger = json.loads((root / "ledger-latest.json").read_bytes())
        result["ledger_verified_at"] = ledger["verified_at"]
        result["ledger_state"] = (
            ledger["state"] if ledger["state"] in ("verified", "failed") else "unknown"
        )
    except (OSError, ValueError, KeyError):
        pass
    return result


def observe(config, root, settings, provider_probe=None):
    probe = provider_probe or ProviderProbe(
        OllamaProvider(settings) if settings.provider == "ollama" else FakeProvider()
    )
    provider = probe.get()
    state = (
        "synthetic"
        if settings.provider == "fake"
        else (
            "ready"
            if provider["reachability"] == "reachable" and provider["model_available"]
            else "model_unavailable"
            if provider["reachability"] == "reachable"
            else "unreachable"
        )
    )
    metrics = resources(root)
    return dict(
        observed_at=timestamp(),
        database=database_state(settings),
        provider=state,
        provider_checked_at=provider["checked_at"],
        model_residency=model_residency(settings),
        **api_state(config.port),
        private_proxy=api_state(config.proxy_port) if config.tailnet_proxy else None,
        resources=metrics,
        discretionary_pause=discretionary_reason(metrics),
        backup=backup_state(root, config.backup_fresh_hours),
    )
