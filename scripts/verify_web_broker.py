"""Disposable Docker isolation controls; public pilot only with explicit flag.

Outputs fixed states/counts, never source text, contact headers or approved private URLs.
"""

import argparse
import json
import subprocess
import time
from pathlib import Path
from uuid import uuid4

from ada.config import Settings
from ada.web_broker import DockerWebBroker, docker_environment
from ada.web_policy import target, user_agent


def verify(manifest, output, public_pilot=False):
    broker = DockerWebBroker(manifest)
    if not broker.available:
        raise SystemExit("Isolated broker unavailable; web research remains disabled")
    name = "ada-web-control-" + uuid4().hex
    env = docker_environment()

    def docker(*args, timeout=20):
        return subprocess.run(
            ["docker", *args], env=env, check=True, capture_output=True, timeout=timeout
        )

    report = {
        "version": "ada-web-isolation-validation-v1",
        "image_id": broker.image,
        "proof": broker.proof,
    }
    try:
        # Synthetic reachable private service; never an application DB/provider endpoint.
        docker(
            "run",
            "--detach",
            "--rm",
            "--name",
            name,
            "--read-only",
            "--log-driver=none",
            "--cap-drop=ALL",
            "--user=65534",
            "--pids-limit=8",
            "--memory=64m",
            "--network=bridge",
            "--entrypoint=python",
            broker.image,
            "-E",
            "-s",
            "-m",
            "http.server",
            "18080",
            "--bind",
            "0.0.0.0",
        )
        address = json.loads(docker("inspect", name).stdout)[0]["NetworkSettings"]["Networks"][
            "bridge"
        ]["IPAddress"]
        probe = (
            "import socket;s=socket.create_connection((" + repr(address) + ",18080),2);s.close()"
        )
        docker(
            "run",
            "--rm",
            "--read-only",
            "--cap-drop=ALL",
            "--user=65534",
            "--log-driver=none",
            "--entrypoint=python",
            broker.image,
            "-E",
            "-s",
            "-c",
            probe,
        )
        restricted = broker._execute(
            {
                "selftest": True,
                "address": "1.1.1.1",
                "expires_at": int(time.time() * 1000) + 60000,
                "receipt_key": str(uuid4()),
                "validation_target": [address, 18080],
            }
        )
        assert restricted["all_blocked"] and restricted["blocked_targets"] == 10
        report["private_canary_reachable_without_firewall"] = True
        report["same_private_canary_blocked_inside_broker"] = True
        report["restricted_proof"] = restricted
        if public_pilot:
            agent = user_agent(Settings().web_operator_contact)
            report["public_pilot"] = []
            for kind, value in (
                ("fetch", "https://docs.python.org/3/library/zoneinfo.html"),
                ("search", "Jupiter"),
            ):
                result = broker.fetch(
                    kind,
                    target(kind, value),
                    int(time.time() * 1000) + 60000,
                    str(uuid4()),
                    agent if kind == "search" else user_agent(),
                )
                report["public_pilot"].append(
                    {
                        "kind": kind,
                        "state": result["state"],
                        "code": result.get("code"),
                        "text_codepoints": len(result.get("text", "")),
                        "snippet_count": len(result.get("snippets", [])),
                        "extraction_truncated": result.get("extraction_truncated", False),
                    }
                )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(
            json.dumps(
                {"isolation": "passed", "public_pilot": report.get("public_pilot", "not requested")}
            )
        )
    finally:
        subprocess.run(
            ["docker", "rm", "--force", name],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, default=Path(".pytest_cache/web-broker-verification.json")
    )
    parser.add_argument(
        "--public-pilot",
        action="store_true",
        help="Send public zoneinfo URL/Jupiter query with configured approved contact",
    )
    args = parser.parse_args()
    verify(args.manifest, args.output, args.public_pilot)
