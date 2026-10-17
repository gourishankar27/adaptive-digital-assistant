"""Bounded relevance over original input text; no generated factual promotion."""

import re

from ada.retrieval import STOP_WORDS


def terms(value):
    return set(re.findall(r"\w{3,}", value.casefold())) - STOP_WORDS


def rank_history(rows, query):
    # Keep the newest complete pair first for local conversational coherence.
    # Only original user wording supplies relevance; assistant inventions cannot.
    keys = terms(query)
    return rows[:1] + sorted(
        rows[1:],
        key=lambda row: (-len(keys & terms(row.messages[-1]["content"])), -row.base_revision),
    )


def rank_original_sources(episodes, query):
    """Input is already owner/scope/time/freshness checked by LearningService."""
    keys, ranked, seen = terms(query), [], set()
    for episode, sources in episodes:
        for source in sources:
            evidence = source["evidence"]
            identity = (evidence["source_version_id"], evidence["span_start"], evidence["span_end"])
            if identity in seen or source["trust_class"] == "model_generated":
                continue
            coverage = len(keys & terms(evidence["quote"]))
            if coverage < 2 or len(evidence["quote"].encode()) > 600:
                continue
            seen.add(identity)
            ranked.append((coverage, episode.created_at, episode.id, episode, source))
    ranked.sort(key=lambda value: (-value[0], -value[1], value[2]))
    return [(row[3], row[4]) for row in ranked[:2]]
