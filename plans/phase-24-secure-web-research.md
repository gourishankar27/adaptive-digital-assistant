# Phase 24 — secure, cited web research

Status: **Proposed; planning only.** Inputs: 20 readiness, 12 approval/receipt
protocol, 18 privacy/erasure, G-24/G-33. Follow [shared rules](FUTURE-ROADMAP.md).
21/22 improve remote sign-in but do not block isolated server security tests.

## Outcome and privacy boundary

Ask ADA to research a public question, inspect/edit the exact outgoing query or
URL, approve it, and receive a sourced answer. Search/fetch services necessarily
learn that approved request and network metadata. Private conversations, memory,
files and credentials remain local by default. No claim of zero disclosure.
No logged-in browsing, file upload, form submission, purchases or external writes.

## Checkpoints

- **A — egress boundary before tools.** Define a narrow broker receiving only an
  approved canonical query/URL, target policy, expiry, byte/time budget and opaque
  receipt key. It has no private database, local model context, file access or
  inherited application secrets. Enforce OS/container/network restrictions on a
  demonstrably isolated implementation; a Python helper named sandbox is not
  sufficient. Network budget is separate from, and cannot create extra inference
  capacity. Disable the feature if isolation cannot be demonstrated on the host.
- **B — public URL pilot.** Start with HTTPS static text/HTML from an allowlisted
  documentation/public-information pilot. Validate scheme, normalized hostname,
  port, DNS A/AAAA answers and actual connected address; reject loopback, private,
  link-local, metadata, multicast, IPv4-mapped IPv6 and tailnet/internal ranges.
  Revalidate/pin targets and TLS identity on every redirect; bound hops, decoded
  bytes, redirects, time and concurrent fetches. No JS, subresources, arbitrary
  protocols, authentication cookies, local proxies or automatic crawling.
- **C — approved search.** Select one provider/API after checking current terms,
  price, privacy/retention and key handling; this plan does not choose a purchase.
  Preview the exact query/parameters and recipient service. By default queries
  derive from the current public research request, not private memory. If private
  context is requested, show the exact selected disclosure and obtain new approval.
  Redaction is assistance, not proof of anonymization. Model-generated URLs/query
  parameters receive the same checks; every follow-on outbound call needs matching
  unexpired authority. Only the dedicated provider key goes to its intended API.
- **D — untrusted evidence.** Parse in bounded isolated code; retain an owned
  immutable extracted-text snapshot with fetched/final URL, retrieval time,
  content hash, parser version, trust/origin and license/terms metadata. Propose
  versioned W web citations, distinct from old M/D/C labels; export typed additive
  contracts and bind quoted spans to the exact saved text. Search snippets remain
  snippets, not proof that a page was read. Report freshness and inaccessible pages.
  Never execute page instructions or promote page text to personal factual memory.
- **E — owner experience.** Research controls show what leaves, pending approval,
  cancelled/expired/blocked/rate-limited/partial states and the receipt. Original
  answers/citations replay from saved snapshots; they do not refetch automatically.
  An owner can explicitly save a research note or ask for further reading.
  Agent output cannot authorize another tool. Admin sees counts/status only.

## Proposed data/interfaces and limits

Versioned web tool arguments/approval fingerprints, outbound receipt, source
snapshot and citation cards; exact routes selected at implementation. Proposed
pilot bounds: three pages per approved research run, three redirects/page,
1 MiB decoded/page, 15 s fetch deadline and no automatic retry after an unknown
outcome. Tune after tests; no broad session-wide disclosure permission by default.
Request size and MIME/decompression bounds apply before parser/model context.
Include all snapshots/receipts containing private URLs in erasure/backup/epoch
inventory. Operational logs contain counts/fixed codes, not full URLs/queries.
Full query/URL audit belongs only in the authenticated encrypted/private owner view.

## Failure tests and exit

Test DNS rebinding/TOCTOU, redirects into localhost/private/VPN/metadata addresses,
alternate numeric/encoded hosts, IPv6, proxy environment inheritance, credential
URLs, compressed bombs, hostile MIME/HTML, Unicode spoofing, injection requesting
private-memory exfiltration and injected tool approval. Assert the broker cannot
contact PostgreSQL/Ollama/private HTTP or read secrets. Test revoked approval/
device, deletion during fetch, expired source, duplicate response and crash before
receipt. Stub first, then authorized public pilot with minimal approved data.

Exit with demonstrated network restrictions and disclosure controls, typed saved
citations and documented residual risk. A prompt filter is never the isolation
boundary. No web access is enabled by this planning document.

Primary design guidance: OWASP [SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
and [LLM prompt injection](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).
