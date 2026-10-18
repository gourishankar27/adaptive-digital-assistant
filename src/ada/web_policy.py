"""Closed public pilot policy; copied verbatim into the secret-free broker image."""

import hashlib
import ipaddress
import json
import re
from urllib.parse import quote, unquote, urlencode, urlsplit

VERSION = "ada-web-research-v1"
PARSER = "ada-static-text-v1"
HOSTS = ("docs.python.org", "en.wikipedia.org")
MAX_BYTES = 1048576
MAX_TEXT = 32768
DEADLINE = 15
DISCLOSURE = (
    "Only this exact approved GET URL, a fixed public User-Agent and network metadata leave ADA. "
    "DNS operators see the hostname. The destination can retain the request/IP under its policy. "
    "No chat history, saved memory, files, credentials or cookies are attached. "
    "Anything you type into this query or URL is disclosed; redaction is not anonymization. "
    "Redirects require a new preview and approval. No automatic follow-up or retry. "
    "Network I/O is limited to 15 seconds; DNS/setup has a separate bounded allowance."
)
TERMS = {
    "docs.python.org": {
        "license": "Python documentation license; individual material may differ",
        "terms_url": "https://docs.python.org/3/license.html",
        "privacy_url": "https://www.python.org/privacy/",
    },
    "en.wikipedia.org": {
        "license": "Wikimedia attribution/share-alike terms; individual material may differ",
        "terms_url": "https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use",
        "privacy_url": "https://foundation.wikimedia.org/wiki/Policy:Privacy_policy",
    },
}


def user_agent(contact=None):
    if contact is not None:
        if (
            not isinstance(contact, str)
            or not 3 <= len(contact) <= 180
            or not contact.isascii()
            or any(c in contact for c in "()\r\n\x00")
        ):
            raise WebBlocked("invalid_operator_contact")
        if contact.startswith("https://"):
            url = urlsplit(contact)
            if (
                not url.hostname
                or url.username
                or url.password
                or url.query
                or url.fragment
                or url.port not in (None, 443)
            ):
                raise WebBlocked("invalid_operator_contact")
        elif not re.fullmatch(r"[A-Za-z0-9._+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", contact):
            raise WebBlocked("invalid_operator_contact")
    return (
        "ADA-PublicResearchBot/1.0 ("
        + (contact or "private owner-approved documentation pilot")
        + ")"
    )


class WebBlocked(ValueError):
    """Only fixed reason codes may leave the private owner view."""


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value):
    return hashlib.sha256((VERSION + "\0" + canonical(value)).encode()).hexdigest()


def public_ip(value):
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        raise WebBlocked("invalid_address") from None
    if (
        not ip.is_global
        or ip.is_multicast
        or ip.is_unspecified
        or (
            isinstance(ip, ipaddress.IPv6Address)
            and (ip.ipv4_mapped is not None or ip.sixtofour is not None or ip.teredo is not None)
        )
    ):
        raise WebBlocked("non_public_address")
    return str(ip)


def target(kind, value):
    if not isinstance(value, str) or not 1 <= len(value) <= 2048:
        raise WebBlocked("invalid_target")
    if any(ord(c) < 32 or ord(c) == 127 for c in value) or "\\" in value:
        raise WebBlocked("invalid_target")
    if kind == "search":
        query = value.strip()
        if not query or len(query) > 300:
            raise WebBlocked("invalid_query")
        return "https://en.wikipedia.org/w/rest.php/v1/search/page?" + urlencode(
            {"q": query, "limit": "3"}
        )
    if kind != "fetch":
        raise WebBlocked("unsupported_action")
    try:
        url = urlsplit(value)
        host = url.hostname
        port = url.port
    except ValueError:
        raise WebBlocked("invalid_url") from None
    if (
        url.scheme != "https"
        or host not in HOSTS
        or not host.isascii()
        or url.username is not None
        or url.password is not None
        or url.netloc.lower() not in (host, host + ":443")
        or port not in (None, 443)
        or url.query
        or url.fragment
    ):
        raise WebBlocked("url_outside_pilot")
    decoded = unquote(url.path, errors="strict")
    if (
        any(ord(c) < 32 or ord(c) == 127 for c in decoded)
        or any(c in decoded for c in ("\\", "?", "#", ":"))
        or any(part in (".", "..") for part in decoded.split("/"))
    ):
        raise WebBlocked("invalid_path")
    if host == "docs.python.org":
        allowed = decoded.startswith("/3/") and decoded.endswith((".html", "/"))
    else:
        allowed = decoded.startswith("/wiki/") and len(decoded) > len("/wiki/")
    if not allowed or "%" in decoded:
        raise WebBlocked("path_outside_pilot")
    return "https://" + host + quote(decoded, safe="/-._~()")


def validate_url(kind, url):
    if kind == "fetch":
        if target(kind, url) != url:
            raise WebBlocked("noncanonical_target")
    elif kind == "search":
        from urllib.parse import parse_qs

        parsed = urlsplit(url)
        query = parse_qs(parsed.query, strict_parsing=True)
        if set(query) != {"q", "limit"} or len(query["q"]) != 1 or query["limit"] != ["3"]:
            raise WebBlocked("invalid_search_parameters")
        if target(kind, query["q"][0]) != url:
            raise WebBlocked("noncanonical_target")
    else:
        raise WebBlocked("unsupported_action")
    return urlsplit(url)
