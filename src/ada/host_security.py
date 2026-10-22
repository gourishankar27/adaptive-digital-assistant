"""Local operator identity, user-scoped DPAPI and process-owned singleton leases."""

import ctypes
import json
import os
import subprocess
import time
from pathlib import Path
from uuid import uuid4


class HostError(Exception):
    """Only fixed codes from this module enter operational receipts."""


def sid():
    if os.name != "nt":
        raise HostError("windows_required")
    result = subprocess.run(
        ["whoami.exe", "/user", "/fo", "csv", "/nh"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    import csv
    import re

    value = next(csv.reader(result.stdout.splitlines()))[-1]
    if not re.fullmatch(r"S-1-[0-9-]+", value):
        raise HostError("identity_unavailable")
    return value


def acl(path, action="Check"):
    helper = Path(__file__).resolve().parents[2] / "scripts/host-acl.ps1"
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(helper),
            "-Action",
            action,
            "-Path",
            str(Path(path).resolve()),
        ],
        capture_output=True,
        timeout=15,
    )
    if result.returncode:
        raise HostError("protected_directory_required")


def no_redirect(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise HostError("redirected_path_refused")
    return path


def private_directory(path):
    path = no_redirect(path)
    path.mkdir(parents=True, exist_ok=True)
    acl(path, "Protect")
    return path


def _crypt(data, decrypt=False):
    if os.name != "nt":
        raise HostError("windows_required")
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    def blob(value):
        buffer = (ctypes.c_ubyte * len(value)).from_buffer_copy(value)
        return Blob(len(value), buffer), buffer

    source, source_buffer = blob(data)
    entropy, entropy_buffer = blob(b"ADA-unattended-backup-key-v1")
    output = Blob()
    crypto = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if decrypt:
        function = crypto.CryptUnprotectData
        function.argtypes = [
            ctypes.POINTER(Blob),
            ctypes.c_void_p,
            ctypes.POINTER(Blob),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(Blob),
        ]
        ok = function(
            ctypes.byref(source), None, ctypes.byref(entropy), None, None, 1, ctypes.byref(output)
        )
    else:
        function = crypto.CryptProtectData
        function.argtypes = [
            ctypes.POINTER(Blob),
            wintypes.LPCWSTR,
            ctypes.POINTER(Blob),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(Blob),
        ]
        # UI forbidden; deliberately no CRYPTPROTECT_LOCAL_MACHINE.
        ok = function(
            ctypes.byref(source),
            "ADA backup key",
            ctypes.byref(entropy),
            None,
            None,
            1,
            ctypes.byref(output),
        )
    if not ok:
        raise HostError("backup_key_unavailable")
    try:
        return ctypes.string_at(output.data, output.size)
    finally:
        kernel.LocalFree(output.data)


def protect(data):
    return _crypt(data)


def unprotect(data):
    return _crypt(data, decrypt=True)


class Singleton:
    """Kernel file lock, not a timestamp that can steal a live worker's lease."""

    def __init__(self, path):
        self.path, self.stream = Path(path), None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("a+b")
        self.stream.seek(0)
        if self.path.stat().st_size == 0:
            self.stream.write(b"0")
            self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise HostError("already_running") from None
        return self

    def __exit__(self, *_):
        if self.stream is not None:
            self.stream.close()  # Kernel releases on close or process death.


def atomic_json(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + "." + uuid4().hex + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        deadline = time.monotonic() + 3
        while True:
            try:
                os.replace(temporary, path)
                break
            except PermissionError as error:
                # Windows readers may temporarily omit FILE_SHARE_DELETE. Keep the
                # old complete receipt visible; retry only sharing/access collisions.
                if (
                    os.name != "nt"
                    or getattr(error, "winerror", None) not in (5, 32, 33)
                    or time.monotonic() >= deadline
                ):
                    raise
                time.sleep(0.05)
    finally:
        temporary.unlink(missing_ok=True)


def timestamp():
    return int(time.time() * 1000)


class OwnedJob:
    """Windows closes only our assigned child tree if its supervisor dies."""

    def __init__(self):
        from ctypes import wintypes

        class Basic(ctypes.Structure):
            _fields_ = [
                ("process_time", ctypes.c_longlong),
                ("job_time", ctypes.c_longlong),
                ("flags", wintypes.DWORD),
                ("min_working", ctypes.c_size_t),
                ("max_working", ctypes.c_size_t),
                ("active", wintypes.DWORD),
                ("affinity", ctypes.c_size_t),
                ("priority", wintypes.DWORD),
                ("scheduling", wintypes.DWORD),
            ]

        class Extended(ctypes.Structure):
            _fields_ = [
                ("basic", Basic),
                ("io", ctypes.c_ulonglong * 6),
                ("process_memory", ctypes.c_size_t),
                ("job_memory", ctypes.c_size_t),
                ("peak_process", ctypes.c_size_t),
                ("peak_job", ctypes.c_size_t),
            ]

        if os.name != "nt":
            raise HostError("windows_required")
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.handle or not self.kernel.SetInformationJobObject(
            self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            self.close()
            raise HostError("owned_process_job_unavailable")

    def assign(self, process):
        # CPython3.12 Windows Popen owns this exact process handle; never enumerate/kill by PID.
        if not self.kernel.AssignProcessToJobObject(self.handle, int(process._handle)):
            process.terminate()
            process.wait(timeout=10)
            raise HostError("owned_process_job_assignment_failed")

    def close(self):
        if getattr(self, "handle", None):
            self.kernel.CloseHandle(self.handle)
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
