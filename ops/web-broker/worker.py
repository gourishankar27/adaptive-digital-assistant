"""One approved public request, restricted by an independent network namespace.

No ADA imports, database, model context, credentials, environment proxy or host mount.
This entrypoint runs only in the dedicated immutable container image.
"""

import ctypes
import errno
import hashlib
import http.client
import ipaddress
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import time
from html.parser import HTMLParser
from urllib.parse import quote, urljoin

from web_policy import (
    DEADLINE,
    MAX_BYTES,
    MAX_TEXT,
    PARSER,
    TERMS,
    WebBlocked,
    public_ip,
    target,
    user_agent,
    validate_url,
)


def restrict(address):
    # These rules affect only this disposable container's network namespace.
    for binary in ("iptables", "ip6tables"):
        subprocess.run([binary, "-P", "OUTPUT", "DROP"], check=True, capture_output=True)
    subprocess.run(
        ["iptables", "-A", "OUTPUT", "-p", "tcp", "-d", address, "--dport", "443", "-j", "ACCEPT"],
        check=True,
        capture_output=True,
    )
    libc = ctypes.CDLL(None, use_errno=True)
    for capability in range(41):
        if libc.prctl(24, capability, 0, 0, 0) != 0:  # PR_CAPBSET_DROP
            raise WebBlocked("capability_drop_failed")
    os.setgroups([])
    os.setgid(65534)
    os.setuid(65534)
    if libc.prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
        raise WebBlocked("privilege_drop_failed")
    with open("/proc/self/status") as stream:
        status = stream.read()
    if "CapEff:\t0000000000000000" not in status or "NoNewPrivs:\t1" not in status:
        raise WebBlocked("privilege_drop_failed")


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.parts, self.depth = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "template", "noscript", "iframe", "svg", "head"):
            self.skip.append(tag)
        if tag not in ("br", "img", "meta", "link", "hr", "input", "source", "wbr"):
            self.depth += 1
        if self.depth > 128:
            raise WebBlocked("html_depth_bound")
        if tag in ("p", "div", "li", "br", "h1", "h2", "h3", "tr") and not self.skip:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if self.skip and tag == self.skip[-1]:
            self.skip.pop()
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)
        if len(self.parts) > 32768:
            raise WebBlocked("html_fragment_bound")


def clean(value):
    # Strip terminal controls as well as NUL; retain Unicode code-point offsets.
    value = "".join(c for c in value if c in "\n\t" or (ord(c) >= 32 and not 127 <= ord(c) < 160))
    return "\n".join(" ".join(line.split()) for line in value.splitlines() if line.strip())


def extract(body, mime, kind):
    try:
        text = body.decode("utf-8", errors="strict")
    except UnicodeError:
        raise WebBlocked("unsupported_text_encoding") from None
    if kind == "search":
        if mime != "application/json":
            raise WebBlocked("unsupported_mime")
        value = json.loads(text)
        items = []
        for page in value.get("pages", [])[:3]:
            key, title = page.get("key", ""), page.get("title", "")
            try:
                url = target("fetch", "https://en.wikipedia.org/wiki/" + quote(key, safe=""))
            except WebBlocked:
                continue
            parser = TextParser()
            parser.feed(str(page.get("excerpt", ""))[:6000])
            items.append(
                {
                    "title": clean(title)[:300],
                    "url": url,
                    "snippet": clean("".join(parser.parts))[:1000],
                }
            )
        return "", items
    if mime == "text/html":
        parser = TextParser()
        parser.feed(text)
        text = "".join(parser.parts)
    elif mime != "text/plain":
        raise WebBlocked("unsupported_mime")
    text = clean(text)
    if not text:
        raise WebBlocked("extracted_text_bound")
    return text, []


class PinnedConnection(http.client.HTTPSConnection):
    def __init__(self, host, address, deadline):
        super().__init__(
            host,
            timeout=max(0.1, deadline - time.monotonic()),
            context=ssl.create_default_context(),
        )
        self.address, self.deadline = address, deadline

    def connect(self):
        # Never resolve again between approval resolution and connect.
        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw.settimeout(max(0.1, self.deadline - time.monotonic()))
        try:
            raw.connect((self.address, 443))
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
            if public_ip(self.sock.getpeername()[0]) != self.address:
                raise WebBlocked("connected_address_mismatch")
        except BaseException:
            raw.close()
            raise


def fetch(request):
    kind, url, address = request["kind"], request["url"], request["address"]
    parsed = validate_url(kind, url)
    agent = request["user_agent"]
    if (
        not re.fullmatch(r"ADA-PublicResearchBot/1\.0 \([^()\r\n\x00]{3,180}\)", agent)
        or not agent.isascii()
    ):
        raise WebBlocked("invalid_user_agent")
    if (
        parsed.hostname == "en.wikipedia.org"
        and "private owner-approved documentation pilot" in agent
    ):
        raise WebBlocked("research_provider_contact_required")
    if parsed.hostname == "docs.python.org" and agent != user_agent():
        raise WebBlocked("unexpected_contact_disclosure")
    deadline = time.monotonic() + DEADLINE
    connection = PinnedConnection(parsed.hostname, address, deadline)
    try:
        path = parsed.path + (("?" + parsed.query) if parsed.query else "")
        connection.request(
            "GET",
            path,
            headers={
                "User-Agent": agent,
                "Accept-Encoding": "identity",
                "Accept": "text/html,text/plain,application/json",
            },
        )
        response = connection.getresponse()
        if response.status in (301, 302, 303, 307, 308):
            candidate = urljoin(url, response.getheader("Location", ""))
            # A redirect does not inherit approval. Even a valid destination needs a new call.
            return {
                "state": "redirect_requires_approval",
                "redirect_url": target("fetch", candidate),
            }
        if response.status == 429:
            return {"state": "rate_limited"}
        if response.status != 200:
            return {"state": "inaccessible"}
        if response.getheader("Content-Encoding", "identity").lower() != "identity":
            raise WebBlocked("compressed_response_blocked")
        declared = response.getheader("Content-Length")
        if declared is not None and (not declared.isdigit() or int(declared) > MAX_BYTES):
            raise WebBlocked("response_byte_bound")
        mime = response.getheader("Content-Type", "").split(";", 1)[0].strip().lower()
        if mime not in (("application/json",) if kind == "search" else ("text/plain", "text/html")):
            raise WebBlocked("unsupported_mime")
        body = bytearray()
        while True:
            if time.monotonic() >= deadline:
                raise WebBlocked("fetch_deadline")
            stream_socket = connection.sock or response.fp.raw._sock
            stream_socket.settimeout(max(0.1, deadline - time.monotonic()))
            block = response.read1(min(16384, MAX_BYTES + 1 - len(body)))
            if not block:
                break
            body.extend(block)
            if len(body) > MAX_BYTES:
                raise WebBlocked("response_byte_bound")
        text, snippets = extract(bytes(body), mime, kind)
        return {
            "state": "completed",
            "kind": kind,
            "fetched_url": url,
            "final_url": url,
            "retrieved_at": int(time.time() * 1000),
            "parser_version": PARSER,
            "text": text[:MAX_TEXT],
            "content_hash": hashlib.sha256(text[:MAX_TEXT].encode()).hexdigest(),
            "extraction_truncated": len(text) > MAX_TEXT,
            "snippets": snippets,
            "terms": TERMS[parsed.hostname],
            "mime": mime,
            "source_origin": "public_web",
            "trust_class": "untrusted_web",
            "last_modified": clean(response.getheader("Last-Modified", ""))[:100],
        }
    finally:
        connection.close()


def read_only_filesystem():
    try:
        # /tmp is world-writable: EACCES under /broker would prove only UID permissions.
        with open("/tmp/ada-read-only-probe", "w") as stream:
            stream.write("synthetic")
    except OSError as exc:
        return exc.errno == errno.EROFS
    return False


def selftest(validation_target=None):
    blocked = []
    targets = [
        ("127.0.0.1", 5432),
        ("127.0.0.1", 5433),
        ("127.0.0.1", 11434),
        ("127.0.0.1", 8000),
        ("169.254.169.254", 80),
        ("192.168.1.1", 8000),
        ("100.64.0.1", 443),
        ("172.17.0.1", 5433),
        ("1.1.1.1", 80),
    ]
    if validation_target is not None:
        host, port = validation_target
        if not ipaddress.ip_address(host).is_private or port != 18080:
            raise WebBlocked("invalid_validation_target")
        targets.append((host, port))
    for host, port in targets:
        with socket.socket() as sock:
            sock.settimeout(0.12)
            try:
                sock.connect((host, port))
            except OSError:
                blocked.append(True)
            else:
                blocked.append(False)
    with open("/proc/self/status") as stream:
        status = stream.read()
    return {
        "state": "isolated",
        "blocked_targets": len(blocked),
        "all_blocked": all(blocked),
        "uid": os.getuid(),
        "read_only": read_only_filesystem(),
        "seccomp": "Seccomp:\t2" in status,
        "bounding_set_empty": "CapBnd:\t0000000000000000" in status,
        "no_private_env": not any(
            value
            and (key.upper().startswith(("ADA_", "POSTGRES")) or key.lower().endswith("_proxy"))
            for key, value in os.environ.items()
        ),
        "host_files_absent": not any(
            os.path.exists(p) for p in ("/host", "/var/run/docker.sock", "/broker/.env")
        ),
    }


def main():
    request = json.loads(sys.stdin.buffer.read(8193))
    if set(request) - {
        "kind",
        "url",
        "address",
        "expires_at",
        "receipt_key",
        "selftest",
        "user_agent",
        "validation_target",
    }:
        raise WebBlocked("broker_input_invalid")
    address = public_ip(request["address"])
    if ipaddress.ip_address(address).version != 4:
        raise WebBlocked("ipv6_transport_unavailable")
    if not 0 < request["expires_at"] - int(time.time() * 1000) <= 300000:
        raise WebBlocked("approval_expired")
    restrict(address)
    return selftest(request.get("validation_target")) if request.get("selftest") else fetch(request)


if __name__ == "__main__":
    try:
        result = main()
    except WebBlocked as exc:
        result = {"state": "blocked", "code": str(exc)}
    except Exception:
        result = {"state": "failed", "code": "public_fetch_failed"}
    print(json.dumps(result, ensure_ascii=True, separators=(",", ":")), flush=True)
