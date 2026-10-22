"""Idle policy is bounded consent, never model/action authority."""

import pytest


@pytest.mark.parametrize(
    "change",
    [
        {"idle_seconds": 899},
        {"nightly_seconds": 601},
        {"max_jobs": 4},
        {"unit_seconds": 31},
        {"unit_seconds": 20, "nightly_seconds": 10},
        {"job_kinds": ["shell"]},
        {"source_types": ["all_private_data"]},
        {"source_types": ["completed_user_turns"], "automatic_completed_turns": False},
        {"allowed_start": 1200, "allowed_end": 100},
        {"timezone": "../private"},
        {"enabled": True, "scope_ids": []},
        {"lookback_days": 31},
    ],
)
def test_policy_rejects_unbounded_or_implicit_authority(change):
    from ada.reflection_contracts import ReflectionSettings

    with pytest.raises(ValueError):
        ReflectionSettings(**change)


def test_default_idle_policy_is_off_and_has_only_review_drafts():
    from ada.reflection_contracts import ReflectionSettings

    value = ReflectionSettings()
    assert not value.enabled and not value.automatic_completed_turns
    assert value.idle_seconds == 900 and value.nightly_seconds == 600 and value.max_jobs == 3
    assert set(value.job_kinds) == {"report", "question"}
    assert value.source_types == ["user_notes"]
