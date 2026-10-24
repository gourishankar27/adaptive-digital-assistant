"""Prepare the pinned, optional Android speech evaluation bundle. Never installs an APK."""

import argparse
import hashlib
import json
import shutil
import struct
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AAR_SHA = "633c24321e06b1fe79feafa03ea16cbc0f8a286641e2da3559bac91bdb13bd96"
ARCHIVES = {
    "kws.tar.bz2": (
        "kws-models/sherpa-onnx-kws-zipformer-gigaspeech-3.3M-2024-01-01.tar.bz2",
        "f170013b4716e41b62b9bfd809687c207cef798ef9bc6534d524e17af9b6561a",
        17626723,
    ),
    "kokoro.tar.bz2": (
        "tts-models/kokoro-en-v0_19.tar.bz2",
        "912804855a04745fa77a30be545b3f9a5d15c4d66db00b88cbcd4921df605ac7",
        319625534,
    ),
    "sherpa-onnx-1.13.8.aar": ("v1.13.8/sherpa-onnx-1.13.8.aar", AAR_SHA, 50129134),
}
ASR_BASE = "https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-en-20M-2023-02-17/resolve/d42f2d9f7ca24806fb667456a18a9f1b60f70d16/"


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def download(url, path, sha, size, enabled):
    if not path.exists():
        if not enabled:
            raise ValueError("Missing public artifact; use --download explicitly")
        temporary = path.with_suffix(path.suffix + ".partial")
        try:
            with urllib.request.urlopen(url, timeout=60) as source, temporary.open("xb") as target:
                total = 0
                while data := source.read(1024 * 1024):
                    total += len(data)
                    if total > size:
                        raise ValueError("Public artifact exceeded pinned size")
                    target.write(data)
            if temporary.stat().st_size != size or digest(temporary) != sha:
                raise ValueError("Public artifact integrity mismatch")
            temporary.rename(path)
        finally:
            temporary.unlink(missing_ok=True)
    if path.stat().st_size != size or digest(path) != sha:
        raise ValueError("Pinned artifact changed")


def prepare(cache, output, network=False):
    cache, output = cache.resolve(), output.resolve()
    owned = (ROOT / "build").resolve()
    if (
        not cache.is_relative_to(owned)
        or not output.is_relative_to(owned)
        or output == owned
        or cache == owned
    ):
        raise ValueError("Use separate directories inside repository build/")
    cache.mkdir(parents=True, exist_ok=True)
    catalogue = ROOT / "ops/speech-runtime/catalogue.json"
    raw = catalogue.read_bytes()
    if (
        hashlib.sha256(raw).hexdigest()
        != "403b9e4b16a87eedaec87bcd5219c02f7f2bc44e274092fc2a237cc0a9036038"
    ):
        raise ValueError("Reviewed catalogue changed")
    files = {f["path"]: f for f in json.loads(raw)["files"]}
    for name, (relative, sha, size) in ARCHIVES.items():
        download(
            "https://github.com/k2-fsa/sherpa-onnx/releases/download/" + relative,
            cache / name,
            sha,
            size,
            network,
        )
    for name, metadata in files.items():
        if name.startswith("asr/"):
            download(
                ASR_BASE + Path(name).name,
                cache / Path(name).name,
                metadata["sha256"],
                metadata["bytes"],
                network,
            )
    destination = output / "assets/speech-models"
    destination.mkdir(parents=True, exist_ok=True)
    for group, archive in (("kws", "kws.tar.bz2"), ("tts", "kokoro.tar.bz2")):
        with tarfile.open(cache / archive) as source:
            for member in source:
                parts = member.name.split("/")
                name = group + "/" + "/".join(parts[1:])
                if name not in files or name == "kws/keywords.txt":
                    continue
                if not member.isfile() or member.size != files[name]["bytes"]:
                    raise ValueError("Unexpected model archive member")
                target = destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.extractfile(member) as stream, target.open("wb") as out:
                    shutil.copyfileobj(stream, out)
    for name in files:
        if name.startswith("asr/"):
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(cache / Path(name).name, target)
    (destination / "kws/keywords.txt").write_text(
        "\u2581HE LL O \u2581A D A :1.8 #0.5 @HELLO_ADA\n", encoding="utf-8", newline="\n"
    )
    for name, metadata in files.items():
        file = destination / name
        if file.stat().st_size != metadata["bytes"] or digest(file) != metadata["sha256"]:
            raise ValueError("Model bundle differs from pinned catalogue")
    shutil.copyfile(catalogue, destination / "catalogue.json")
    aar = cache / "sherpa-onnx-1.13.8.aar"
    with zipfile.ZipFile(aar) as archive:
        for name in archive.namelist():
            if not name.startswith("jni/arm64-v8a/") or not name.endswith(".so"):
                continue
            data = archive.read(name)
            if data[:6] != b"\x7fELF\x02\x01" or struct.unpack_from("<H", data, 18)[0] != 183:
                raise ValueError("Expected arm64 ELF")
            offset = struct.unpack_from("<Q", data, 32)[0]
            size, count = struct.unpack_from("<HH", data, 54)
            loads = [
                struct.unpack_from("<Q", data, offset + i * size + 48)[0]
                for i in range(count)
                if struct.unpack_from("<I", data, offset + i * size)[0] == 1
            ]
            if not loads or min(loads) < 16384:
                raise ValueError("Native speech requires 16KiB load alignment")
    if aar.resolve() != (output / aar.name).resolve():
        shutil.copyfile(aar, output / aar.name)
    test_assets = output / "test-assets"
    test_assets.mkdir(parents=True, exist_ok=True)
    download(
        ASR_BASE + "test_wavs/0.wav",
        test_assets / "speech-public.wav",
        "6bc58a4efdf20daac252b6b1502632601a71efe0308f6757dc1eda34891a7e4f",
        212044,
        network,
    )
    print("Pinned speech evaluation bundle verified; no APK installed or model activated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "build/phase32")
    parser.add_argument("--output", type=Path, default=ROOT / "build/private-voice")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    prepare(args.cache, args.output, args.download)
