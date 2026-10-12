"""Public synthetic gate comparison; it does not measure model/user preference accuracy."""

import json
from pathlib import Path

import pytest
from conftest import make_conversation
from test_learning import config, inbox, observation, scope_of


@pytest.mark.parametrize(
    "case,texts,confidence,expected",
    [
        ("single_explicit", ["Please use concise planning replies."], "explicit_statement", 1),
        ("copied_exchange", ["Brief explanations help."] * 3, "repeated_observation", 1),
        (
            "weak_guesses",
            ["Tentative planning guess.", "Tentative coding guess.", "Tentative review guess."],
            "weak_inference",
            0,
        ),
        (
            "three_independent",
            [
                "Brief planning notes help.",
                "Concise coding explanations please.",
                "Compact reviews are useful.",
            ],
            "repeated_observation",
            3,
        ),
        (
            "four_independent",
            [
                "Brief planning notes help.",
                "Concise coding explanations please.",
                "Compact reviews are useful.",
                "Short testing feedback please.",
            ],
            "repeated_observation",
            4,
        ),
    ],
)
def test_measured_threshold_comparison(harness, case, texts, confidence, expected):
    h = harness
    cid, _ = make_conversation(h)
    sid = scope_of(h, cid)
    config(h, sid)
    for text in texts:
        assert observation(h, cid, text, confidence)[0].status_code == 201
    results = []
    for threshold in (3, 4):
        h["app"].state.learning.threshold = threshold
        state = inbox(h, sid)
        proposal = state["proposals"][0]
        assert proposal["independent_count"] == expected
        assert proposal["eligible"] == (expected >= threshold)
        assert state["learned"] == []
        results.append(
            {
                "threshold": threshold,
                "observed_count": proposal["independent_count"],
                "eligible": proposal["eligible"],
                "automatic_promotions": len(state["learned"]),
            }
        )
    destination = (
        Path(__file__).resolve().parents[1]
        / ".pytest_cache"
        / "phase15"
        / f"evaluation-{h['backend']}-{case}.json"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            {
                "case": case,
                "backend": h["backend"],
                "provider": "recording_fixture",
                "results": results,
                "limit": "Selected annotations and public synthetic interactions, not model precision or proof of preference",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
