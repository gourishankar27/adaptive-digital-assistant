"""Run from the repository root after changing API schemas."""

import json
from pathlib import Path

from ada.api import create_app
from ada.config import Settings
from ada.providers import FakeProvider

app = create_app(Settings(provider="fake"), FakeProvider())
destination = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"
destination.parent.mkdir(exist_ok=True)
destination.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print(destination)
