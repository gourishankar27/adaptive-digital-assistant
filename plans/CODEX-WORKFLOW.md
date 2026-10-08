# Running one phase with Codex

## Inspect

Read the root instructions, current README/architecture/OpenAPI, CURRENT-STATE,
STANDARDS, STATUS and the requested phase. Inspect relevant source and tests. Read
the scoped client instructions once those directories exist. Check dependencies
against actual code, not only checkboxes in a plan. Inspect local changes first.

Summarize the implementation boundary and identify current behavior that must
survive. A frontend phase may require a typed contract from a prior phase; it does
not authorize a new auth scheme or an unrequested document backend.

## Establish the baseline

Run the relevant existing checks. For the current Windows failure, close 02A with
the targeted installer tests and the user's full PostgreSQL suite. Record known
warnings separately. If a tool, database or device is unavailable, record that
limit and complete independent authorized work. Do not claim an unavailable check
passed or ask for permission to do already authorized, reversible work.

When a missing prerequisite changes the product's scope, explain the concrete gap
and request steering. Do not silently implement an entire prerequisite phase.

## Implement bounded checkpoints

Follow one checkpoint at a time. Add invariants/failure tests for new write or
authorization paths first. Keep fake providers and client fixtures explicit.
Validate versions against official documentation; pin the resulting dependencies.
Keep network/model work outside transactions. Preserve source and prompt history.

A checkpoint should leave an executable flow. For example, complete Android
connection/authentication before building a source-detail screen that assumes an
authenticated request. The admin dashboard needs the server's admin policy before
it can request cross-user metadata.

## Verify

Run the phase-specific checks plus STANDARDS checks for the affected subsystems.
Use migrated disposable databases. Exercise a real HTTP adapter for an integration
flow, not only screenshots generated from fixtures. Client failure tests include
reconnect, account switching and duplicate submission. Database/provider failures
must not produce fake success or a second side effect.

Use measured API metadata for admin views. Do not invent GPU utilization, live
token streams, missing source cards or background task completion.

## Record and stop

Update the implemented API contract, capabilities and documentation where needed.
Add a status/work-log entry with code version, exact checks, target environments
and remaining verification. Preserve earlier evidence and its provenance. Record
an architectural deviation in DECISIONS with rationale and impact.

Report the concrete resulting behavior and any installation/migration step.
Leave later phase files planned. Stop at the selected phase. Deployment, external
messages, publication and real external tool effects require an explicit request;
a future roadmap entry is not that request.

## Review checklist

- Does the product call a real, authorized API for every enabled control?
- Can account/scope changes expose a prior user's cache, trace or pending payload?
- Do reconnects preserve IDs/options and original citations?
- Are timestamp/code-point conversions correct across Python, Kotlin and JSON?
- Are new source origins honest, and is model output still untrusted?
- Do migrations preserve populated history and prompt/version compatibility?
- Are model calls outside transactions and capacity limits effective?
- Are failures visible and recoverable without fabricated success?
- Does the recorded validation distinguish local, target, fake and real-model runs?
- Is each new requirement traceable to the selected phase, a current invariant or
  an explicit user instruction?

## Work-log entry format

```markdown
### YYYY-MM-DD — phase/checkpoint — code version
Scope:
Changed behavior/files:
Data/API/prompt changes:
Checks actually run and results:
Checks skipped/blocked and reason:
Windows/PostgreSQL/device/model evidence:
Remaining issues:
Next eligible checkpoint:
```

Use UTC timestamps for machine evidence and note a displayed timezone when it
matters. Do not paste raw private transcripts or credentials into this log.
