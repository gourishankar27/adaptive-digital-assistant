"""A separate native probe is required; these tests only verify adapter boundaries."""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest

from ada.config import Settings
from ada.providers import ProviderError
from ada.reflection_provider import OllamaReflectionProvider

DIGEST = "a" * 64


def settings(**values):
    return Settings(
        _env_file=None,
        provider="fake",
        ollama_model="public-test",
        reflection_model_digest=DIGEST,
        **values,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://example.org",
        "http://192.168.1.2:11434",
        "http://localhost:11434",
        "http://127.0.0.1/path",
        "http://x@127.0.0.1",
    ],
)
def test_idle_model_rejects_nonliteral_or_credentialed_destinations(url):
    with pytest.raises(ValueError):
        OllamaReflectionProvider(settings(ollama_url=url))


def test_changed_digest_blocks_inference_before_post():
    calls = []

    def respond(request):
        calls.append(request.method)
        return httpx.Response(200, json={"models": [{"name": "public-test", "digest": "b" * 64}]})

    provider = OllamaReflectionProvider(settings(), httpx.MockTransport(respond))
    with pytest.raises(ProviderError) as error:
        provider.complete([], {}, threading.Event(), 1)
    assert error.value.code == "reflection_model_changed" and calls == ["GET"]


@pytest.mark.parametrize(
    "extra", [{}, {"tool_calls": [{"name": "write"}]}, {"thinking": "private reasoning"}]
)
def test_structured_stream_never_executes_tools_or_returns_reasoning(extra):
    calls = []

    def respond(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"models": [{"name": "public-test", "digest": DIGEST}]})
        message = {
            "role": "assistant",
            "content": '{"sections":[],"tags":[],"omissions":[]}',
            **extra,
        }
        return httpx.Response(
            200,
            content=json.dumps({"model": "public-test", "message": message, "done": True}) + "\n",
        )

    provider = OllamaReflectionProvider(settings(), httpx.MockTransport(respond))
    if extra:
        with pytest.raises(ProviderError):
            provider.complete([], {}, threading.Event(), 1)
    else:
        assert provider.complete([], {}, threading.Event(), 1).model == "public-test"
    body = json.loads(calls[-1].content)
    assert body["think"] is False and body["stream"] is True and "tools" not in body


def test_real_loopback_read_stall_is_bounded_after_cancel():
    entered = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            raw = json.dumps({"models": [{"name": "public-test", "digest": DIGEST}]}).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200)
            self.end_headers()
            entered.set()
            time.sleep(1.5)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    cancel = threading.Event()
    timer = threading.Thread(target=lambda: (entered.wait(2), cancel.set()), daemon=True)
    timer.start()
    try:
        provider = OllamaReflectionProvider(
            settings(ollama_url=f"http://127.0.0.1:{server.server_port}")
        )
        start = time.monotonic()
        with pytest.raises(ProviderError):
            provider.complete([], {}, cancel, 3)
        assert cancel.is_set() and time.monotonic() - start < 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(2)
        timer.join(2)


def test_trickling_metadata_cannot_extend_the_cancel_deadline():
    entered = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            entered.set()
            try:
                for _ in range(50):
                    self.wfile.write(b" ")
                    self.wfile.flush()
                    time.sleep(0.05)
                self.wfile.write(b'{"models":[]}')
            except (OSError, ConnectionError):
                pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    cancel = threading.Event()
    timer = threading.Thread(target=lambda: (entered.wait(2), cancel.set()), daemon=True)
    timer.start()
    try:
        provider = OllamaReflectionProvider(
            settings(ollama_url=f"http://127.0.0.1:{server.server_port}")
        )
        start = time.monotonic()
        with pytest.raises(ProviderError):
            provider.complete([], {}, cancel, 5)
        assert cancel.is_set() and time.monotonic() - start < 1.5
    finally:
        server.shutdown()
        server.server_close()
        thread.join(2)
        timer.join(2)
