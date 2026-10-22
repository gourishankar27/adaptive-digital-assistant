"""Frozen public evaluation provenance and disposable-runner safety guards."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_quality_manifest_rejects_native_paths_changed_content_and_versions(tmp_path):
    evaluation = module("phase23_evaluation", "evaluate_answer_quality.py")
    original = json.loads(evaluation.MANIFEST.read_text(encoding="utf-8"))
    assert len(evaluation.load_corpus()["cases"]) == 16
    manifest = tmp_path / "manifest.json"
    evaluation.MANIFEST = manifest
    for key, value in (
        ("corpus", "evaluations\\answer-quality-phase23-v1.json"),
        ("corpus", "../private.json"),
        ("sha256", "0" * 64),
        ("version", "future"),
    ):
        changed = original | {key: value}
        manifest.write_text(json.dumps(changed), encoding="utf-8")
        with pytest.raises(ValueError):
            evaluation.load_corpus()


def test_quality_canonical_digest_handles_windows_newlines(tmp_path):
    evaluation = module("phase23_digest", "evaluate_answer_quality.py")
    path = tmp_path / "corpus.json"
    path.write_bytes(b'{\n "synthetic": true\n}\n')
    original = evaluation.digest(path)
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert evaluation.digest(path) == original


def test_validation_runner_rejects_physical_device_and_primary_package(monkeypatch):
    runner = module("phase23_validation_guard", "verify_password_android.py")
    monkeypatch.setenv("ADA_TEST_DATABASE_URL", "dedicated-test-database")
    with pytest.raises(SystemExit, match="explicit expected device model"):
        runner.run("physical-device")
    with pytest.raises(SystemExit, match="separate validation application"):
        runner.run("emulator-5584", package="dev.ada.assistant.debug")
