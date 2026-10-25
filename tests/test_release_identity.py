"""Release labels agree across packages without changing protocol/schema identity."""

import json
import re
import tomllib
from pathlib import Path

from ada.api import create_app
from ada.config import Settings
from ada.providers import FakeProvider
from ada.schema import SCHEMA_HEAD
from ada.version import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_release_identity_and_protocol_versions_are_independent():
    release = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    web = json.loads((ROOT / "apps/admin-web/package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "apps/admin-web/package-lock.json").read_text(encoding="utf-8"))
    android = (ROOT / "apps/android/app/build.gradle.kts").read_text(encoding="utf-8")
    assert release["version"] == __version__ == project["project"]["version"] == web["version"]
    assert lock["version"] == lock["packages"][""]["version"] == __version__
    assert re.search(r'versionName = "([^"]+)"', android)[1] == __version__
    assert int(re.search(r"versionCode = (\d+)", android)[1]) == release["android_version_code"]
    assert release["server_schema"] == SCHEMA_HEAD and release["api_version"] == "v1"
    schema = create_app(
        Settings(provider="fake", database_url="sqlite://"), FakeProvider()
    ).openapi()
    assert schema["info"]["version"] == __version__
    assert "/v1/conversations" in schema["paths"]
