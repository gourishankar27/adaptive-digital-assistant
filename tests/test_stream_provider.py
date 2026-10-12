import json
import threading

import httpx
import pytest

from ada.config import Settings
from ada.providers import Completion, ProviderError
from ada.stream_provider import StreamingOllamaProvider


class Fragments(httpx.SyncByteStream):
    def __init__(self, chunks):
        self.chunks = chunks
        self.closed = False

    def __iter__(self):
        yield from self.chunks

    def close(self):
        self.closed = True


def frame(text="", done=False, **extra):
    return (
        json.dumps({"message": {"content": text}, "done": done, **extra}, ensure_ascii=False) + "\n"
    ).encode()


def test_native_stream_fragmented_unicode_and_final_usage():
    wire = frame("🫖 hello ") + frame("there", True, prompt_eval_count=12, eval_count=4)
    body = Fragments([wire[i : i + 2] for i in range(0, len(wire), 2)])

    def handle(request):
        payload = json.loads(request.content)
        assert payload["stream"] is True and payload["think"] is False
        assert payload["options"] == {"num_ctx": 8192, "num_predict": 512}
        assert request.headers["Accept-Encoding"] == "identity"
        return httpx.Response(200, stream=body)

    stream = StreamingOllamaProvider(Settings(), httpx.MockTransport(handle)).stream(
        [], threading.Event()
    )
    assert list(stream) == [
        "🫖 hello ",
        "there",
        Completion("🫖 hello there", "qwen3.8:27b", 12, 4),
    ]
    assert body.closed


@pytest.mark.parametrize(
    "wire",
    [
        frame("uncompleted"),
        frame("", True),
        b"x" * 16385,
        frame("\u0000", True),
        frame("x", True, eval_count=True),
        (
            json.dumps({"done": True, "message": {"content": "x", "tool_calls": [{}]}}) + "\n"
        ).encode(),
    ],
)
def test_native_stream_rejects_incomplete_untrusted_and_unbounded_frames(wire):
    body = Fragments([wire])
    provider = StreamingOllamaProvider(
        Settings(), httpx.MockTransport(lambda _: httpx.Response(200, stream=body))
    )
    with pytest.raises(ProviderError):
        list(provider.stream([], threading.Event()))
    assert body.closed


def test_cancelled_adapter_closes_connection_without_completion():
    body = Fragments([frame("one"), frame("two", True)])
    signal = threading.Event()
    provider = StreamingOllamaProvider(
        Settings(), httpx.MockTransport(lambda _: httpx.Response(200, stream=body))
    )
    stream = provider.stream([], signal)
    assert next(stream) == "one"
    signal.set()
    assert list(stream) == [] and body.closed


def test_terminal_frame_without_trailing_newline():
    body = Fragments([frame("complete", True).rstrip(b"\n")])
    provider = StreamingOllamaProvider(
        Settings(), httpx.MockTransport(lambda _: httpx.Response(200, stream=body))
    )
    assert list(provider.stream([], threading.Event()))[-1].text == "complete"
