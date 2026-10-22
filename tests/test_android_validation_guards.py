"""Install guards must fail before touching a normal app or an unselected phone."""

import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def validator(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    module = importlib.import_module("verify_password_android")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "synthetic-sdk"))
    monkeypatch.setenv("ADA_TEST_DATABASE_URL", "postgresql://synthetic-test-only")
    return module


def test_physical_device_requires_explicit_model_before_any_adb_call(validator, monkeypatch):
    monkeypatch.setattr(validator.subprocess, "run", lambda *a, **k: pytest.fail("Unexpected ADB"))
    with pytest.raises(SystemExit, match="explicit expected device model"):
        validator.run("public-fixture-device")


def test_normal_application_id_is_never_an_install_target(validator, monkeypatch):
    monkeypatch.setattr(validator.subprocess, "run", lambda *a, **k: pytest.fail("Unexpected ADB"))
    with pytest.raises(SystemExit, match="separate validation application ID"):
        validator.run("emulator-5554", package="dev.ada.assistant.debug")


def test_wrong_physical_model_stops_before_install_or_fixture(validator, monkeypatch):
    calls = []

    def command(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(stdout="Different public fixture model\n")

    monkeypatch.setattr(validator.subprocess, "run", command)
    with pytest.raises(SystemExit, match="explicitly expected model"):
        validator.run("public-fixture-device", physical_model="SM-S721U1")
    assert len(calls) == 1 and calls[0][-2:] == ["getprop", "ro.product.model"]


def test_apk_contents_are_checked_even_when_metadata_claims_validation(
    validator, monkeypatch, tmp_path
):
    package = "dev.ada.validation.guard.debug"
    for folder, name, identity in (
        ("debug", "app-debug.apk", package),
        ("androidTest/debug", "app-debug-androidTest.apk", package + ".test"),
    ):
        directory = tmp_path / "apps/android/app/build/outputs/apk" / folder
        directory.mkdir(parents=True)
        (directory / "output-metadata.json").write_text(json.dumps({"applicationId": identity}))
        (directory / name).write_bytes(b"public synthetic APK placeholder")
    (tmp_path / ".pytest_cache").mkdir()
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    calls = []

    class Socket:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def bind(self, address):
            pass

    def command(args, **kwargs):
        calls.append([str(arg) for arg in args])
        return SimpleNamespace(stdout="package: name='dev.ada.assistant.debug'\n")

    monkeypatch.setattr(validator.socket, "socket", Socket)
    monkeypatch.setattr(validator.subprocess, "run", command)
    monkeypatch.setattr(
        validator.subprocess, "Popen", lambda *a, **k: pytest.fail("Unexpected server")
    )
    with pytest.raises(RuntimeError, match="APK contents do not match"):
        validator.run("emulator-5554", package=package)
    assert all("install" not in args for args in calls)
    assert all("dev.ada.assistant.debug" not in args for args in calls)
    assert not list((tmp_path / ".pytest_cache").iterdir())
