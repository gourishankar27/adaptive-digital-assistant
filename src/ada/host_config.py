"""Protected local host configuration, separate from API and private content state."""

import json
import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ada.host_security import HostError, acl, no_redirect, private_directory, sid


class HostConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    format: str = "ada-host-v1"
    owner_sid: str
    profile: str
    repository: str
    port: int = Field(default=8000, ge=1024, le=65535)
    tailnet_proxy: bool = False
    proxy_port: int = Field(default=18764, ge=1024, le=65535)
    pg_bin: str
    backup_directory: str
    poll_seconds: int = Field(default=30, ge=2, le=300)
    startup_attempts: int = Field(default=8, ge=1, le=12)
    crash_limit: int = Field(default=5, ge=1, le=10)
    stable_seconds: int = Field(default=300, ge=10, le=3600)
    shutdown_seconds: int = Field(default=30, ge=5, le=180)
    quiet_seconds: int = Field(default=30, ge=5, le=600)
    daily_backup_time: str = Field(default="03:00", pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")
    backup_fresh_hours: int = Field(default=26, ge=1, le=48)
    prune_backups: bool = False

    @field_validator("profile", "repository", "pg_bin", "backup_directory")
    @classmethod
    def absolute_path(cls, value):
        if any(char in value for char in ('"', "\n", "\r", "\0")) or not Path(value).is_absolute():
            raise ValueError("Absolute literal path required")
        return no_redirect(value).resolve().as_posix()


def load_config(path):
    path = no_redirect(path).resolve()
    acl(path.parent)
    try:
        if path.stat().st_size > 16384:
            raise HostError("invalid_configuration")
        config = HostConfig.model_validate_json(path.read_bytes())
        if config.format != "ada-host-v1" or config.prune_backups:
            raise HostError("unsupported_configuration")
        if (
            config.owner_sid != sid()
            or Path(config.profile) != Path(os.environ["LOCALAPPDATA"]).resolve()
        ):
            raise HostError("configuration_identity_mismatch")
        if Path(config.backup_directory) != Path(config.profile) / "ADA/backups":
            raise HostError("backup_profile_mismatch")
        if not (Path(config.repository) / ".venv/Scripts/python.exe").is_file():
            raise HostError("repository_runtime_missing")
        return config, path.parent
    except (ValueError, KeyError, OSError):
        raise HostError("invalid_configuration") from None


def initialize(path, repository, pg_bin, port=8000):
    root = private_directory(Path(path).absolute().parent)
    config = HostConfig(
        owner_sid=sid(),
        profile=Path(os.environ["LOCALAPPDATA"]).resolve().as_posix(),
        repository=Path(repository).resolve().as_posix(),
        pg_bin=Path(pg_bin).resolve().as_posix(),
        backup_directory=(Path(os.environ["LOCALAPPDATA"]) / "ADA/backups").resolve().as_posix(),
        port=port,
    )
    with (root / Path(path).name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(config.model_dump(), stream, indent=2)
    return config
