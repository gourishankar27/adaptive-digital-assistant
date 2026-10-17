# Phase 22 — password login and revocable sessions

Status: **Implemented checkpoints A–E; isolated verification and target limits recorded in STATUS/WORKLOG. No live enrollment, migration or deployment.** Inputs: 20 readiness, 18 device lifecycle,
G-21/G-28/G-32.21 is required before remote login, not local disposable tests.
Follow [shared rules](FUTURE-ROADMAP.md). Existing owner IDs/admin grants survive.

## Outcome

Normal Android and admin sign-in asks for server, username and password. Session
credentials are created and renewed internally; users do not copy bearer tokens.
Legacy CLI/device tokens remain a compatibility/recovery path during migration.
No public signup, email provider, account sharing or automatic admin enrollment.

## Checkpoints

- **A — account migration.** Add a distinct normalized login identifier and
  password verifier, not a password in `User.name` or a token digest field.
  Preserve display names and owner UUIDs; detect case/Unicode normalization
  collisions before operator assignment. Existing accounts start password-login
  disabled until their local operator sets a password using a hidden prompt.
  Never derive passwords from names/tokens. Local CLI recovery is retained.
- **B — password verification.** Use pinned Argon2id with unique salt and
  benchmarked memory/time cost, bounded concurrent hashing, constant-time library
  verification and rehash-on-success. Support passphrases/password managers/paste;
  propose minimum 15 characters without MFA and a documented generous upper bound.
  No forced composition tricks, silent truncation or unsolicited online password
  checks. Generic responses and dummy verification protect account enumeration.
- **C — session lifecycle.** Use server-revocable opaque access credentials and
  rotating refresh families (proposed 15 min access/30 day absolute refresh lifetime,
  7 day idle expiry, configurable after measurements). Persist verifiers only.
  Reuse of an old refresh revokes its family; concurrent refreshes and lost delivery
  need explicit bounded recovery, never permanent plaintext token escrow.
  Define logout current/all, password change/reset, expiry, device revocation,
  refresh and restore-quarantine behavior. Reset revokes password-session families;
  separately issued legacy/device credentials retain their explicit revocation
  policy and are visible to the operator. No session can mint an admin grant.
- **D — HTTP integration.** The current middleware rejects unauthenticated `/v1`
  calls before rate admission. Add only exact login/refresh routes to a dedicated
  pre-auth path with byte/time limits, global/IP/account-attempt throttles and
  bounded hash concurrency before expensive work. Trust forwarded IPs only from
  configured loopback proxies. Bound identifier spray; avoid permanent lockout
  that lets an attacker disable another account. All ordinary private routes
  still require fresh server authentication, including SSE batches.
- **E — both clients.** Android stores refresh material in Keystore, access in
  memory, and never persists the password. Browser uses Secure/HttpOnly/SameSite
  host-only cookies, exact same-origin/CSRF checks and no JS-readable storage.
  This is an explicit planned extension to the current bearer-only web transport;
  update scoped instructions when implemented. Reject conflicting cookie/bearer
  identities; preserve the separate legacy bearer adapter. Admin dashboard stays
  read-only except authentication operations.401/refresh/epoch/account switches
  clear private state and never replay a POST automatically.

## Proposed data and interfaces

Account password metadata, session/refresh family verifiers, revocation/version
and minimal rate/audit metadata; exact endpoint names are selected at implementation
and exported in OpenAPI. Password mutation requires recent authentication or local
operator authority. Reuse18 device labels/revocation concepts without coupling
password login to the optional general device-enrollment switch. Restore must
disable recovered session authority and require explicit credential recovery.
Update erasure inventory classifications, schema-versioned backup and clients.

## Failure tests and exit

Before writes, test brute force/resource exhaustion, nonexistent/disabled users,
duplicate/colliding identifiers, refresh theft/reuse/race/crash, logout/reset
during streams, cookie fixation/CSRF, cross-origin redirect, stale sessions,
conflicting principals, token compatibility, wrong-owner pending recovery and
non-admin sign-in. Use PostgreSQL concurrency/populated upgrades and actual HTTP/
browser cookie tests; no credentials in snapshots/logs. Run affected Android/web
checks. Exit with complete sign-in→reopen→renew→logout/revoke flows on both clients,
documented limits and no manual token handling in ordinary login. Physical tests
remain deferred; no live account/password is changed by planning.

Design references: OWASP [password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html),
[authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
and [session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html).

## Implementation record

See [the password/session guide](../docs/PASSWORD-LOGIN-AND-SESSIONS.md) for exact
routes, normalization, Argon2 profile, admission/rotation limits, lost-delivery policy,
Android v12 compatibility, HTTPS cookies/CSRF, legacy credential boundaries and
0015/v1–0016/v2 restore quarantine. Physical/release HTTPS and manual review remain
separate gates. Dated actual checks/skips are appended to STATUS and WORKLOG.
