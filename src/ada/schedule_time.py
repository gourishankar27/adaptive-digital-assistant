"""Pinned IANA rules; finite UTC plans are reviewed before becoming authority."""

import re
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from zoneinfo import ZoneInfo

import tzdata

DAY = 86400000
TIMEZONE_DATA = "tzdata-" + tzdata.__version__


def zone(name):
    if not re.fullmatch(r"[A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+)*", name):
        raise ValueError("Invalid IANA timezone")
    try:
        with files("tzdata.zoneinfo").joinpath(*name.split("/")).open("rb") as stream:
            return ZoneInfo.from_file(stream, key=name)
    except (OSError, ValueError):
        raise ValueError("Unavailable IANA timezone") from None


def resolve_plan(definition):
    try:
        return _resolve_plan(definition)
    except OverflowError:
        raise ValueError("Scheduled local time is out of range") from None


def _resolve_plan(definition):
    tz = zone(definition.timezone)
    local = datetime.strptime(definition.start_local, "%Y-%m-%dT%H:%M")
    minute = local.hour * 60 + local.minute
    if not definition.allowed_start <= minute < definition.allowed_end:
        raise ValueError("Scheduled local time must fall within allowed hours")
    step = {"once": 0, "daily": 1, "weekly": 7}[definition.frequency]
    result = []
    for n in range(definition.count):
        current = local + timedelta(days=n * step)
        candidates = {}
        for fold in (0, 1):
            aware = current.replace(tzinfo=tz, fold=fold)
            utc = aware.astimezone(timezone.utc)
            if utc.astimezone(tz).replace(tzinfo=None) == current:
                candidates[int(utc.timestamp() * 1000)] = fold
        if not candidates:
            if definition.gap == "reject" or definition.frequency == "once":
                raise ValueError("Scheduled local time is nonexistent")
            continue
        if len(candidates) > 1 and definition.fold == "reject":
            raise ValueError("Scheduled local time is ambiguous; select first or second")
        at = (max if definition.fold == "second" else min)(candidates)
        if at < int(definition.expires_at.timestamp() * 1000):
            result.append({"at": at, "local": current.strftime("%Y-%m-%dT%H:%M")})
    if not result:
        raise ValueError("No eligible occurrence before expiry")
    return result


def allowed(definition, instant):
    value = datetime.fromtimestamp(instant / 1000, timezone.utc).astimezone(
        zone(definition.timezone)
    )
    return definition.allowed_start <= value.hour * 60 + value.minute < definition.allowed_end
