# ADA — Phase 0

A Python backend for a Windows 11 laptop, shared by multiple authenticated users.
Ollama runs the language model. Each user can create several private personality
profiles; a conversation freezes its chosen profile. Everyone shares model
weights, never conversation history or personality context.

This is a working server foundation. It includes persistent text chat, an HTTP
API, a CLI client, PostgreSQL migrations, authentication, request retries, and
tests. It does not yet include RAG, extracted claims, tools, Android/iOS apps,
device inference, streaming, or background memory consolidation.

## Your hardware and model

Target: Windows 11 Pro, i9-14900HX, RTX 4090 **Laptop** GPU, 32 GB system RAM.
Ollama's model catalogue lists **`qwen3.8:27b`**, not `qwen3.8:28b`.
The listed model download is 18 GB. NVIDIA lists 16 GB VRAM for the laptop GPU.
Expect that full GPU residency may not fit, especially with context/KV cache;
CPU offloading and throughput must be measured on the actual laptop. Download
size is not a complete memory benchmark. No model weights are bundled here.

Defaults: 8,192 context tokens, at most 512 output tokens, one in-flight model
generation. Thinking is disabled in the adapter for predictable Phase 0 chat.
Change `ADA_OLLAMA_MODEL` in `.env` to any installed compatible chat model.
Multiple accounts do not imply simultaneous GPU generation: busy requests get
HTTP 503 with `Retry-After: 3`. No hidden unbounded queue is created.

Sources checked 2026-10-08:
- https://ollama.com/library/qwen3.8/tags
- https://www.nvidia.com/en-us/geforce/laptops/40-series/
- https://docs.ollama.com/api/chat
- https://docs.ollama.com/faq

## Windows setup

Prerequisites: Python 3.12 with the `py` launcher, Ollama for Windows, and either
Docker Desktop configured for Linux containers or a local PostgreSQL installation.
The Python API and Ollama run natively on Windows. Only PostgreSQL uses the supplied
Docker Compose file. Run commands from the extracted `ada-phase0` directory.

```powershell
.\scripts\setup.ps1
docker compose up -d --wait db
.\.venv\Scripts\python.exe -m alembic upgrade head
ollama pull qwen3.8:27b
.\.venv\Scripts\ada.exe doctor
.\.venv\Scripts\ada.exe create-user Gourishankar
```

The setup script generates a random database password when creating `.env`.
If script execution is disabled by your PowerShell policy, run these equivalent
commands manually; do not change your system policy just for this project:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
Copy-Item .env.example .env
# Edit .env: replace the sample password in both places with your own secret.
```

For native PostgreSQL instead of Docker, create a dedicated `ada` database and
role, configure `ADA_DATABASE_URL`, then run the same migration command. Avoid
putting an unescaped password containing URL punctuation into the connection URL.

`create-user` displays one secret bearer token. Copy it into a password manager.
The database stores only its SHA-256 hash. Tokens have 256 bits of randomness;
this is not a password-hashing design. There is no public registration endpoint.

Start the API in one PowerShell window:

```powershell
.\scripts\start.ps1
# Equivalent:
# .\.venv\Scripts\python.exe -m uvicorn ada.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Start text chat in another window:

```powershell
$env:ADA_TOKEN = 'paste-the-issued-token'
.\.venv\Scripts\ada.exe chat
```

Save the conversation UUID printed by the CLI. After restarting the server:

```powershell
.\.venv\Scripts\ada.exe chat --conversation 'saved-conversation-uuid'
```

The CLI's `/retry` reuses the last request ID. A completed request returns its
stored answer without another model call. After a connection loss, use that
same ID or query request status; a new UUID means a new message.

API explorer: http://127.0.0.1:8000/docs (Authorize with the issued bearer token).
Readiness: http://127.0.0.1:8000/health/ready checks the migrated database, not model
availability. `ada doctor` separately checks Ollama and the configured model tag.

## Try the server before downloading the model

In the server terminal, set `$env:ADA_PROVIDER = 'fake'` before starting it.
Responses are explicitly labelled `[FAKE provider]`; no model runs. Remove that
environment override (`Remove-Item Env:ADA_PROVIDER`) and restart to use Ollama.
Fake mode exercises the same authentication, database, context, and retry path.

## Multiple users and personalities

```powershell
.\.venv\Scripts\ada.exe create-user SecondUser
```

Each person uses their own token. With a token set:

```powershell
$headers = @{Authorization = "Bearer $env:ADA_TOKEN"}
$profile = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/personalities -Headers $headers -ContentType 'application/json' -Body '{"name":"ADA","style":"direct","warmth":"warm","detail":"detailed"}'
$body = @{personality_id = $profile.id; title = 'ADA development'} | ConvertTo-Json
$conversation = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/conversations -Headers $headers -ContentType 'application/json' -Body $body
.\.venv\Scripts\ada.exe chat --conversation $conversation.id
```

Profiles are immutable through the Phase 0 API. Create a new profile to change
style. Existing conversations retain their snapshot and prompt version.
Personality fields cannot set security rules, supply arbitrary system prompts,
or change ownership. User identity is always derived from the bearer token.

## Mobile boundary

`contracts/openapi.json` describes the actual server API. Kotlin/Android and later
Swift/iOS clients will call that same API. They never connect directly to PostgreSQL
or Ollama. See `docs/MOBILE-CONTRACT.md` for the future device-model contract.

Phase 0 binds to loopback. Before real phones connect, provide authenticated HTTPS
through a TLS reverse proxy or an encrypted private network; keep PostgreSQL and
Ollama private. Do not send bearer tokens over ordinary LAN HTTP. No firewall or
public exposure is configured by these scripts. `start.ps1 -ListenAddress ...`
exists for an explicitly configured secure deployment, not as a security setup.

## Failure and restart recovery

- A user event and a `running` request are committed before inference.
- A successful response, assistant event, and conversation revision commit together.
- Provider failure marks the request `failed`; retrying it reuses the user event.
- In-flight requests survive server crashes as `running`. Stop the old server,
  wait beyond the configured timeout plus 60 seconds, then run:

```powershell
.\.venv\Scripts\ada.exe recover-stale --older-than-seconds 300
```

Restart and retry the original ID/content. Recovery fences late responses so an
older attempt cannot overwrite a newer one. The inference itself may run again;
the persistent user turn is deduplicated. There are no external side-effect tools.
A failed old request cannot be retried after a later reply changed the history;
the API returns `retry_history_changed` so the user can submit a fresh request.

Rotate/revoke a leaked token with `ada rotate-token USERNAME`. Revocation applies
to subsequent requests; an already-authorized in-flight request may finish.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests migrations
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations
```

The default suite runs migrated SQLite fixtures for fast feedback. PostgreSQL
cases require a **test** database URL whose role can create/drop schemas:

```powershell
$env:ADA_TEST_DATABASE_URL = 'postgresql+psycopg://testuser:password@127.0.0.1:5432/ada_test'
.\.venv\Scripts\python.exe -m pytest -q
```

Each test creates an isolated random schema and removes it afterward. Never point
tests at your production database. PostgreSQL row locks and partial unique indexes
are tested on PostgreSQL, not inferred from SQLite behavior. See `docs/VALIDATION.md`
for what was actually run while producing this release.

## How the code fits together

- `api.py`: validation, authentication, owner-scoped resources.
- `service.py`: context selection, request reservation, inference, atomic completion.
- `models.py` / `migrations/`: persistent records and tenant-aware foreign keys.
- `providers.py`: replaceable Ollama/fake adapters; no database access.
- `personality.py`: versioned baseline and constrained style configuration.
- `cli.py`: local administration and a remote API client.

Read `docs/ARCHITECTURE.md` before adding memory or tools. Phase 0 deliberately
stores raw conversation evidence without extracting permanent claims.
