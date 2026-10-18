"""Build only the allowlisted secret-free context. No server/network feature activation."""

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "Dockerfile": "ops/web-broker/Dockerfile",
    "worker.py": "ops/web-broker/worker.py",
    "web_policy.py": "src/ada/web_policy.py",
}


def build(output):
    with tempfile.TemporaryDirectory(prefix="ada-public-broker-build-") as directory:
        for target, source in FILES.items():
            shutil.copyfile(ROOT / source, Path(directory) / target)
        hashes = {
            source: hashlib.sha256((ROOT / source).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            for source in FILES.values()
        }
        # Normalize build context to LF on Windows; no repository/env file ever enters it.
        for path in Path(directory).iterdir():
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
        label = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
        result = subprocess.run(
            [
                "docker",
                "build",
                "--label",
                "dev.ada.web-source=" + label,
                "--iidfile",
                str(Path(directory) / "image-id"),
                directory,
            ]
        )
        if result.returncode:
            raise SystemExit("Broker image build failed; feature remains disabled")
        image = (Path(directory) / "image-id").read_text().strip()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps({"image_id": image, "source_label": label, "files": hashes}, indent=2)
            + "\n",
            encoding="utf-8",
        )
        print("Built immutable broker image; not enabled or deployed. Manifest:", output.as_posix())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".pytest_cache/web-broker-image.json")
    build(parser.parse_args().output)
