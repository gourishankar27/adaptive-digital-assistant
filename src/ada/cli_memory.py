"""Remote memory client. The CLI never grants the model a memory write tool."""

import json
import os
import sys
from uuid import UUID, uuid4

import httpx


def add_arguments(sub):
    def remote(parser):
        parser.add_argument("--url", default="http://127.0.0.1:8000")

    scopes = sub.add_parser("scopes", help="Create or list private personal/project scopes")
    scope_commands = scopes.add_subparsers(dest="scope_action", required=True)
    create = scope_commands.add_parser("create")
    remote(create)
    create.add_argument("name")
    create.add_argument("--kind", choices=("personal", "project"), default="project")
    listing = scope_commands.add_parser("list")
    remote(listing)
    listing.add_argument("--limit", type=int, default=100)
    listing.add_argument("--offset", type=int, default=0)

    memory = sub.add_parser("memory", help="Explicit source-backed memory commands")
    commands = memory.add_subparsers(dest="memory_action", required=True)
    for name in ("remember", "correct"):
        command = commands.add_parser(name)
        remote(command)
        command.add_argument("--value", required=True)
        command.add_argument("--claim-id", type=UUID, help="Reuse on retry with identical input")
        evidence = command.add_mutually_exclusive_group(required=True)
        evidence.add_argument("--text", help="Save this exact user statement as evidence first")
        evidence.add_argument("--source-version", type=UUID, help="Cite an existing user source")
        command.add_argument("--source-id", type=UUID, help="Reuse a --text source ID on retry")
        command.add_argument("--start", type=int, help="Unicode code point offset; default 0")
        command.add_argument("--end", type=int, help="Exclusive end; default full content length")
        command.add_argument(
            "--quote", help="Find a unique exact quote instead of entering offsets"
        )
        command.add_argument("--valid-to", help="Optional exclusive ISO 8601 validity end")
        if name == "remember":
            command.add_argument("--scope", type=UUID, required=True)
            command.add_argument("--subject", default="user")
            command.add_argument("--predicate", required=True)
            command.add_argument(
                "--kind", choices=("fact", "preference", "decision"), default="fact"
            )
            command.add_argument(
                "--valid-from", help="ISO 8601 time with timezone; default source time"
            )
        else:
            command.add_argument("claim", type=UUID, help="Claim to supersede")
            command.add_argument(
                "--effective-at", help="ISO 8601 time with timezone; default source time"
            )

    listing = commands.add_parser("list")
    remote(listing)
    listing.add_argument("--scope", required=True, type=UUID)
    time = listing.add_mutually_exclusive_group()
    time.add_argument("--at", help="ISO 8601 valid-time query; default now")
    time.add_argument(
        "--history", action="store_true", help="All versions, including future/expired"
    )
    listing.add_argument("--subject")
    listing.add_argument("--predicate")
    listing.add_argument("--limit", type=int, default=100)
    listing.add_argument("--offset", type=int, default=0)
    show = commands.add_parser("show")
    remote(show)
    show.add_argument("claim", type=UUID)

    search = commands.add_parser("search", help="Retrieve scoped claims without calling the model")
    remote(search)
    search.add_argument("query")
    search.add_argument("--scope", required=True, type=UUID)
    search.add_argument("--at", help="ISO 8601 time with timezone; default now")
    search.add_argument("--limit", type=int, default=8)
    search.add_argument("--budget-bytes", type=int, default=2200)
    trace = commands.add_parser("trace", help="Inspect the evidence snapshot of a chat request")
    remote(trace)
    trace.add_argument("request_id", type=UUID)

    upgrade = sub.add_parser(
        "upgrade-prompt", help="Explicitly update an existing conversation baseline"
    )
    remote(upgrade)
    upgrade.add_argument("conversation", type=UUID)


def run_remote(args, timeout):
    token = os.environ.get("ADA_TOKEN")
    if not token:
        raise ValueError("Set ADA_TOKEN to your issued bearer token.")
    with httpx.Client(
        base_url=args.url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout + 30,
        trust_env=False,
    ) as client:

        def request(method, path, **kwargs):
            response = client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()

        if args.command == "scopes":
            if args.scope_action == "create":
                result = request("POST", "/v1/scopes", json={"name": args.name, "kind": args.kind})
            else:
                result = request(
                    "GET", "/v1/scopes", params={"limit": args.limit, "offset": args.offset}
                )
        elif args.command == "upgrade-prompt":
            result = request("POST", f"/v1/conversations/{args.conversation}/prompt-upgrade")
        elif args.memory_action == "show":
            result = request("GET", f"/v1/claims/{args.claim}")
        elif args.memory_action == "trace":
            result = request("GET", f"/v1/requests/{args.request_id}/retrieval")
        elif args.memory_action == "search":
            body = {"query": args.query, "limit": args.limit, "budget_bytes": args.budget_bytes}
            if args.at is not None:
                body["as_of"] = args.at
            result = request("POST", f"/v1/scopes/{args.scope}/retrieve", json=body)
        elif args.memory_action == "list":
            params = {"history": args.history, "limit": args.limit, "offset": args.offset}
            for key, value in (
                ("as_of", args.at),
                ("subject", args.subject),
                ("predicate", args.predicate),
            ):
                if value is not None:
                    params[key] = value
            result = request("GET", f"/v1/scopes/{args.scope}/claims", params=params)
        else:
            if args.source_id is not None and args.text is None:
                raise ValueError("--source-id requires --text")
            if args.quote is not None and (args.start is not None or args.end is not None):
                raise ValueError("--quote cannot be combined with --start/--end")
            if args.memory_action == "correct":
                old = request("GET", f"/v1/claims/{args.claim}")
                scope_id = old["scope_id"]
            else:
                scope_id = str(args.scope)
            claim_id = str(args.claim_id or uuid4())
            print(f"Claim ID (reuse on retry): {claim_id}", file=sys.stderr)
            if args.text is not None:
                source_id = str(args.source_id or uuid4())
                print(f"Source ID (reuse on retry): {source_id}", file=sys.stderr)
                source = request(
                    "POST",
                    f"/v1/scopes/{scope_id}/notes",
                    json={"source_id": source_id, "content": args.text},
                )
            else:
                source = request("GET", f"/v1/source-versions/{args.source_version}")
            content = source["content"]
            start = args.start if args.start is not None else 0
            end = args.end if args.end is not None else len(content)
            if args.quote is not None:
                start = content.find(args.quote)
                if not args.quote.strip() or start < 0:
                    raise ValueError("--quote must match nonblank source text exactly")
                if content.find(args.quote, start + 1) >= 0:
                    raise ValueError("Quote appears more than once; use --start and --end")
                end = start + len(args.quote)
            body = {
                "claim_id": claim_id,
                "source_version_id": source["id"],
                "span_start": start,
                "span_end": end,
                "value": args.value,
            }
            if args.valid_to is not None:
                body["valid_to"] = args.valid_to
            if args.memory_action == "remember":
                body |= {"subject": args.subject, "predicate": args.predicate, "kind": args.kind}
                if args.valid_from is not None:
                    body["valid_from"] = args.valid_from
                path = f"/v1/scopes/{scope_id}/claims"
            else:
                if args.effective_at is not None:
                    body["effective_at"] = args.effective_at
                path = f"/v1/claims/{args.claim}/supersede"
            result = request("POST", path, json=body)
        print(json.dumps(result, ensure_ascii=False, indent=2))
