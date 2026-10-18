"""Explicit synthetic research transport for the disposable client HTTP fixture only."""

from ada.evidence import content_hash
from ada.models import now_ms
from ada.providers import Completion
from ada.web_policy import PARSER, TERMS


class SyntheticResearchBroker:
    available = True

    def fetch(self, kind, url, expiry, receipt, agent=None):
        text = "😀 ZoneInfo uses IANA timezone data. This is a public synthetic HTTP fixture."
        return {
            "state": "completed",
            "kind": kind,
            "fetched_url": url,
            "final_url": url,
            "retrieved_at": now_ms(),
            "parser_version": PARSER,
            "text": text,
            "content_hash": content_hash(text),
            "terms": TERMS["docs.python.org"],
            "source_origin": "public_web",
            "trust_class": "untrusted_web",
            "snippets": [],
        }


class SyntheticResearchProvider:
    id, model = "synthetic_research", "public-fixture-v1"

    def complete(self, messages):
        return Completion(
            "The synthetic source says ZoneInfo uses IANA timezone data [W1].", self.model
        )


def enable_research_fixture(app):
    app.state.research.broker = SyntheticResearchBroker()
    app.state.research.provider = SyntheticResearchProvider()
    return app
