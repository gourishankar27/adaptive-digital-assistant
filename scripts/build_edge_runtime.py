"""Build the optional CPU-only Android library from verified local archives. No activation."""

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def file_hash(path, algorithm="sha256"):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def elf_alignment(path):
    raw = path.read_bytes()
    if raw[:6] != b"\x7fELF\x02\x01" or struct.unpack_from("<H", raw, 18)[0] != 183:
        raise ValueError("Expected little-endian ELF64 AArch64")
    offset = struct.unpack_from("<Q", raw, 32)[0]
    size, count = struct.unpack_from("<HH", raw, 54)
    loads = [
        struct.unpack_from("<Q", raw, offset + i * size + 48)[0]
        for i in range(count)
        if struct.unpack_from("<I", raw, offset + i * size)[0] == 1
    ]
    if not loads or any(value < 16384 for value in loads):
        raise ValueError("Native PT_LOAD alignment is below 16 KiB")
    return min(loads)


def build(args):
    lock = json.loads((ROOT / "ops/edge-runtime/runtime.lock.json").read_text(encoding="utf-8"))
    if file_hash(args.archive) != lock["archive_sha256"]:
        raise ValueError("llama.cpp archive changed")
    if file_hash(args.ndk_archive, "sha1") != lock["ndk_archive_sha1"]:
        raise ValueError("NDK archive changed")
    for executable, version in ((args.cmake, lock["cmake"]), (args.ninja, lock["ninja"])):
        observed = subprocess.check_output([str(executable), "--version"], text=True)
        if version not in observed.splitlines()[0].split():
            raise ValueError("Use the pinned build tool version")
    directory = args.output.resolve()
    # Build artifacts stay in a new/owned cache, never in the production application tree.
    cache = (ROOT / ".pytest_cache").resolve()
    if not directory.is_relative_to(cache) or directory == cache:
        raise ValueError("Output must be inside the repository .pytest_cache")
    directory.mkdir(parents=True, exist_ok=True)
    source = directory / "source"
    source.mkdir(exist_ok=True)
    with tarfile.open(args.archive) as archive:
        # data filter refuses links outside the extraction root and special files.
        archive.extractall(source, filter="data")
    children = list(source.iterdir())
    if len(children) != 1 or not (children[0] / "include/llama.h").is_file():
        raise ValueError("Unexpected source archive layout")
    ndk = directory / "ndk"
    with zipfile.ZipFile(args.ndk_archive) as archive:
        for member in archive.infolist():
            target = (ndk / member.filename).resolve()
            if not target.is_relative_to(ndk.resolve()):
                raise ValueError("Unsafe NDK archive path")
        archive.extractall(ndk)
    ndk = ndk / "android-ndk-r30"
    if f"Pkg.Revision = {lock['ndk']}" not in (ndk / "source.properties").read_text(
        encoding="utf-8"
    ):
        raise ValueError("Unexpected NDK version")
    build_dir = directory / "build"
    subprocess.run(
        [
            str(args.cmake),
            "-S",
            str(ROOT / "ops/edge-runtime"),
            "-B",
            str(build_dir),
            "-G",
            "Ninja",
            f"-DCMAKE_MAKE_PROGRAM={args.ninja.resolve().as_posix()}",
            f"-DCMAKE_TOOLCHAIN_FILE={(ndk / 'build/cmake/android.toolchain.cmake').as_posix()}",
            "-DANDROID_ABI=arm64-v8a",
            "-DANDROID_PLATFORM=android-28",
            "-DANDROID_STL=c++_static",
            "-DCMAKE_BUILD_TYPE=Release",
            f"-DADA_LLAMA_SOURCE={children[0].as_posix()}",
        ],
        check=True,
    )
    subprocess.run(
        [str(args.cmake), "--build", str(build_dir), "--target", "ada_edge", "-j", "2"], check=True
    )
    library = build_dir / "libada_edge.so"
    alignment = elf_alignment(library)
    native = directory / "jni"
    (native / "arm64-v8a").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(library, native / "arm64-v8a/libada_edge.so")
    notices = native / "notices"
    notices.mkdir(exist_ok=True)
    source_root = children[0]
    license_files = sorted(
        p
        for p in source_root.rglob("*")
        if p.is_file() and p.name.upper().startswith(("LICENSE", "COPYING", "NOTICE"))
    )
    # Preserve the pinned source's notices, including dependencies not linked by
    # this CPU target, rather than omitting attribution from a custom build.
    (notices / "ada-edge-third-party.txt").write_text(
        "\n\n".join(
            str(p.relative_to(source_root).as_posix()) + "\n" + p.read_text(encoding="utf-8")
            for p in license_files
        ),
        encoding="utf-8",
    )
    files = {
        name: hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        for name in ("ops/edge-runtime/native.cpp", "ops/edge-runtime/CMakeLists.txt")
    }
    manifest = {
        "version": lock["version"],
        "runtime": lock["runtime"],
        "source_archive_sha256": lock["archive_sha256"],
        "ndk": lock["ndk"],
        "abi": lock["abi"],
        "library_sha256": file_hash(library),
        "files": files,
        "minimum_load_alignment": alignment,
    }
    (native / "runtime-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "Optional library built; quality activation remains disabled. JNI directory:",
        native.as_posix(),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--ndk-archive", type=Path, required=True)
    parser.add_argument("--cmake", type=Path, required=True)
    parser.add_argument("--ninja", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / ".pytest_cache/edge-runtime")
    build(parser.parse_args())
