"""Calendar intent must survive Windows, DST and restart without guessing."""

from datetime import datetime, timezone

import pytest


def definition(**changes):
    return {
        "kind": "reminder",
        "text": "Review the public sample notebook.",
        "timezone": "America/Phoenix",
        "start_local": "2026-10-20T08:00",
        "frequency": "daily",
        "count": 3,
        "fold": "reject",
        "gap": "skip",
        "allowed_start": 0,
        "allowed_end": 1440,
        "expires_at": "2026-11-10T00:00:00Z",
        "channel": "inbox",
        **changes,
    }


def test_dst_fold_requires_explicit_choice_and_is_previewed():
    from ada.schedule_contracts import ScheduleDefinition
    from ada.schedule_time import resolve_plan

    value = definition(start_local="2026-11-01T01:30", timezone="America/New_York", count=1)
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_plan(ScheduleDefinition(**value))
    a = resolve_plan(ScheduleDefinition(**(value | {"fold": "first"})))
    b = resolve_plan(ScheduleDefinition(**(value | {"fold": "second"})))
    assert b[0]["at"] - a[0]["at"] == 3600000
    assert a[0]["local"] == b[0]["local"] == "2026-11-01T01:30"


def test_spring_gap_is_skipped_without_shifting_wall_clock():
    from ada.schedule_contracts import ScheduleDefinition
    from ada.schedule_time import resolve_plan

    value = definition(
        start_local="2027-03-13T02:30",
        timezone="America/New_York",
        count=3,
        expires_at="2027-03-20T00:00:00Z",
    )
    rows = resolve_plan(ScheduleDefinition(**value))
    assert [r["local"] for r in rows] == ["2027-03-13T02:30", "2027-03-15T02:30"]
    with pytest.raises(ValueError, match="nonexistent"):
        resolve_plan(ScheduleDefinition(**(value | {"gap": "reject"})))


def test_plan_keeps_wall_time_across_dst_and_accepts_non_hour_offsets():
    from ada.schedule_contracts import ScheduleDefinition
    from ada.schedule_time import resolve_plan

    rows = resolve_plan(
        ScheduleDefinition(
            **definition(
                timezone="America/New_York",
                start_local="2026-10-31T08:00",
            )
        )
    )
    assert rows[1]["at"] - rows[0]["at"] == 25 * 3600000
    nepal = resolve_plan(ScheduleDefinition(**definition(timezone="Asia/Kathmandu", count=1)))
    assert datetime.fromtimestamp(nepal[0]["at"] / 1000, timezone.utc).strftime("%H:%M") == "02:15"


@pytest.mark.parametrize(
    "changes",
    [
        {"timezone": "../private"},
        {"count": 101},
        {"channel": "push"},
        {"start_local": "2026-10-20T08:00Z"},
        {"allowed_start": 900, "allowed_end": 800},
        {"kind": "shell"},
        {"frequency": "cron"},
        {"expires_at": "2026-11-10T00:00:00.000001Z"},
    ],
)
def test_reject_unbounded_or_executable_or_unavailable_calendar_intent(changes):
    from ada.schedule_contracts import ScheduleDefinition
    from ada.schedule_time import resolve_plan

    with pytest.raises(ValueError):
        resolve_plan(ScheduleDefinition(**definition(**changes)))


@pytest.mark.parametrize(
    "timezone,start,frequency,count,expiry",
    [
        ("UTC", "9999-12-31T12:00", "daily", 2, "9999-12-31T23:00:00Z"),
        ("UTC", "9999-12-31T12:00", "weekly", 2, "9999-12-31T23:00:00Z"),
        ("Etc/GMT-14", "0001-01-01T00:00", "once", 1, "0001-01-02T00:00:00Z"),
    ],
)
def test_calendar_boundary_is_a_validation_error(timezone, start, frequency, count, expiry):
    from ada.schedule_contracts import ScheduleDefinition
    from ada.schedule_time import resolve_plan

    definition = ScheduleDefinition(
        text="Public calendar boundary probe",
        timezone=timezone,
        start_local=start,
        frequency=frequency,
        count=count,
        expires_at=expiry,
        allowed_start=0,
        allowed_end=1440,
    )
    with pytest.raises(ValueError):
        resolve_plan(definition)
