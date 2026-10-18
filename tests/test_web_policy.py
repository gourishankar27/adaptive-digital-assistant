"""SSRF canonicalization and pinning precede network contact."""

import importlib.util
import socket
from pathlib import Path

import pytest

from ada.web_broker import resolve_public
from ada.web_policy import WebBlocked, public_ip, target, validate_url


@pytest.mark.parametrize(
    "url",
    [
        "http://docs.python.org/3/",
        "https://docs.python.org:444/3/",
        "https://user:pass@docs.python.org/3/",
        "https://127.0.0.1/",
        "https://2130706433/",
        "https://0x7f000001/",
        "https://[::1]/",
        "https://docs.python.org.evil.test/3/",
        "https://docs.python.org./3/",
        "https://dоcs.python.org/3/",
        "https://docs.python.org/3/../private.html",
        "https://docs.python.org/3/%2e%2e/private.html",
        "https://docs.python.org/3/%0d%0a.html",
        "https://docs.python.org/3/index.html?secret=x",
        "https://docs.python.org/3/index.html#x",
        "https://docs.python.org\\@127.0.0.1/3/",
        "https://en.wikipedia.org/wiki/Special:Random",
        "https://en.wikipedia.org/wiki/Special%253ARandom",
    ],
)
def test_unsafe_urls_never_reach_dns(url):
    with pytest.raises((WebBlocked, UnicodeError)):
        target("fetch", url)


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.1.2.3",
        "192.168.1.1",
        "172.17.0.1",
        "169.254.169.254",
        "100.100.100.200",
        "224.0.0.1",
        "::1",
        "fe80::1",
        "fc00::1",
        "::ffff:8.8.8.8",
        "2002:0808:0808::1",
    ],
)
def test_non_public_and_tunnel_addresses_are_blocked(address):
    with pytest.raises(WebBlocked):
        public_ip(address)


def test_dns_checks_every_answer_and_pins_original_public_ip(monkeypatch):
    def answers(*args, **kwargs):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::ffff:127.0.0.1", 443, 0, 0)),
        ]

    monkeypatch.setattr(socket, "getaddrinfo", answers)
    with pytest.raises(WebBlocked):
        resolve_public("docs.python.org")
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **kw: answers()[:1])
    assert resolve_public("docs.python.org") == "8.8.8.8"
    assert (
        target("fetch", "https://DOCS.PYTHON.ORG:443/3/index.html")
        == "https://docs.python.org/3/index.html"
    )
    with pytest.raises(WebBlocked):
        validate_url("search", "https://evil.test/w/rest.php/v1/search/page?q=a&limit=3")


def worker(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "src/ada"))
    spec = importlib.util.spec_from_file_location(
        "public_worker_test", root / "ops/web-broker/worker.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bounded_parser_strips_executable_markup_and_retains_exact_unicode(monkeypatch):
    m = worker(monkeypatch)
    text, snippets = m.extract(
        b'<script>EXFILTRATE</script><p>\xf0\x9f\x98\x80 Zo\xc3\xab uses IANA.</p><img src="http://localhost/private">',
        "text/html",
        "fetch",
    )
    assert text == "😀 Zoë uses IANA." and snippets == []
    with pytest.raises(m.WebBlocked):
        m.extract(b"binary", "application/pdf", "fetch")
    with pytest.raises(m.WebBlocked):
        m.extract(("<div>" * 129).encode(), "text/html", "fetch")


@pytest.mark.parametrize(
    "status,headers,code",
    [
        (302, {"Location": "https://127.0.0.1/private"}, "url_outside_pilot"),
        (
            200,
            {"Content-Type": "text/html", "Content-Encoding": "gzip"},
            "compressed_response_blocked",
        ),
        (200, {"Content-Type": "text/html", "Content-Length": "1048577"}, "response_byte_bound"),
        (200, {"Content-Type": "application/javascript"}, "unsupported_mime"),
    ],
)
def test_redirect_mime_and_bombs_stop_before_read_or_follow(monkeypatch, status, headers, code):
    m = worker(monkeypatch)
    calls = []

    class Response:
        def getheader(self, key, default=None):
            return headers.get(key, default)

        def read1(self, size):
            raise AssertionError("Rejected response body must not be read")

    response = Response()
    response.status = status

    class Connection:
        def __init__(self, *args):
            pass

        def request(self, method, path, headers):
            calls.append((method, path, headers))

        def getresponse(self):
            return response

        def close(self):
            pass

    monkeypatch.setattr(m, "PinnedConnection", Connection)
    with pytest.raises(m.WebBlocked, match=code):
        m.fetch(
            {
                "kind": "fetch",
                "url": "https://docs.python.org/3/index.html",
                "address": "8.8.8.8",
                "user_agent": "ADA-PublicResearchBot/1.0 (private owner-approved documentation pilot)",
            }
        )
    assert len(calls) == 1 and calls[0][0] == "GET"
    assert not {"Cookie", "Authorization", "Proxy-Authorization"} & set(calls[0][2])


def test_contact_header_for_other_recipient_is_rejected_before_connect(monkeypatch):
    m = worker(monkeypatch)
    monkeypatch.setattr(
        m,
        "PinnedConnection",
        lambda *args: pytest.fail("Contact must not leave to another recipient"),
    )
    with pytest.raises(m.WebBlocked, match="unexpected_contact_disclosure"):
        m.fetch(
            {
                "kind": "fetch",
                "url": "https://docs.python.org/3/index.html",
                "address": "8.8.8.8",
                "user_agent": "ADA-PublicResearchBot/1.0 (https://example.org/contact)",
            }
        )


def test_connected_peer_and_tls_identity_are_checked_without_second_dns_lookup(monkeypatch):
    m = worker(monkeypatch)
    context = m.ssl.create_default_context()
    assert context.check_hostname and context.verify_mode == m.ssl.CERT_REQUIRED
    connected = []

    class Raw:
        def settimeout(self, value):
            pass

        def connect(self, address):
            connected.append(address)

        def close(self):
            pass

    class WrongPeer:
        def getpeername(self):
            return ("8.8.4.4", 443)

    def wrap(raw, *, server_hostname):
        assert server_hostname == "docs.python.org"
        return WrongPeer()

    monkeypatch.setattr(context, "wrap_socket", wrap)
    monkeypatch.setattr(m.ssl, "create_default_context", lambda: context)
    monkeypatch.setattr(m.socket, "socket", lambda *args: Raw())
    monkeypatch.setattr(
        m.socket,
        "getaddrinfo",
        lambda *a, **kw: pytest.fail("Pinned connect must not resolve again"),
    )
    connection = m.PinnedConnection("docs.python.org", "8.8.8.8", m.time.monotonic() + 15)
    with pytest.raises(m.WebBlocked, match="connected_address_mismatch"):
        connection.connect()
    assert connected == [("8.8.8.8", 443)]


def test_invalid_public_contact_does_not_echo_database_credentials():
    from ada.config import Settings

    with pytest.raises(ValueError) as error:
        Settings(
            _env_file=None,
            database_url="postgresql://synthetic:synthetic-private-marker@localhost/test",
            web_operator_contact="not-a-public-contact",
        )
    assert "synthetic-private-marker" not in str(error.value)
    assert "not-a-public-contact" not in str(error.value)


def test_stalled_docker_output_and_cleanup_have_deadlines(monkeypatch):
    import io
    import subprocess

    import ada.web_broker as adapter

    class Stalled:
        stdin = io.BytesIO()
        stdout = io.BytesIO()
        killed = False
        waited_with_deadline = False

        def communicate(self, *, input, timeout):
            assert timeout == 23
            self.waited_with_deadline = True
            raise subprocess.TimeoutExpired("synthetic-docker", timeout)

        def poll(self):
            return 0 if self.killed else None

        def kill(self):
            self.killed = True

        def wait(self, *, timeout):
            assert timeout <= 5
            return 0

    process = Stalled()
    cleanup = []

    def remove(command, **kwargs):
        assert command[:3] == ["docker", "rm", "--force"]
        assert kwargs["timeout"] == 10
        cleanup.append(True)
        raise subprocess.TimeoutExpired("synthetic-cleanup", 10)

    monkeypatch.setattr(adapter.subprocess, "Popen", lambda *a, **kw: process)
    monkeypatch.setattr(adapter.subprocess, "run", remove)
    broker = object.__new__(adapter.DockerWebBroker)
    broker.image = "synthetic-immutable-image"
    with pytest.raises(WebBlocked, match="broker_outcome_unknown"):
        broker._execute({"selftest": True})
    assert process.waited_with_deadline and process.killed and cleanup == [True]


@pytest.mark.parametrize("error,expected", [(13, False), (30, True)])
def test_readonly_proof_requires_erofs_in_world_writable_directory(monkeypatch, error, expected):
    m = worker(monkeypatch)

    def write(path, mode):
        assert path.startswith("/tmp/") and mode == "w"
        raise OSError(error, "synthetic filesystem outcome")

    monkeypatch.setattr(m, "open", write, raising=False)
    assert m.read_only_filesystem() is expected
