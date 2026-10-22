"""Native observer contention and concurrent operational receipts stay atomic."""

import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from ada.host_security import atomic_json


@pytest.mark.skipif(os.name != "nt", reason="Windows reader sharing semantics")
def test_transient_open_reader_does_not_kill_receipt_publication(tmp_path):
    target = tmp_path / "state.json"
    atomic_json(target, {"version": 1})
    reader = target.open("rb")

    def release():
        time.sleep(0.15)
        reader.close()

    thread = threading.Thread(target=release)
    thread.start()
    try:
        atomic_json(target, {"version": 2})
    finally:
        thread.join(timeout=3)
        reader.close()
    assert json.loads(target.read_bytes()) == {"version": 2}
    assert not list(tmp_path.glob("*.tmp"))


def test_same_process_concurrent_receipts_never_share_a_temporary_file(tmp_path, monkeypatch):
    target = tmp_path / "state.json"
    barrier = threading.Barrier(2)
    original = os.fsync

    def synchronized_flush(descriptor):
        original(descriptor)
        barrier.wait(timeout=5)

    monkeypatch.setattr(os, "fsync", synchronized_flush)
    values = [{"writer": "first", "value": "a" * 5000}, {"writer": "second", "value": "b" * 5000}]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda value: atomic_json(target, value), values))
    assert json.loads(target.read_bytes()) in values
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.skipif(os.name != "nt", reason="Windows persistent sharing failure")
def test_persistent_reader_failure_is_bounded_and_keeps_previous_receipt(tmp_path):
    target = tmp_path / "state.json"
    atomic_json(target, {"version": 1})
    began = time.monotonic()
    with target.open("rb"):
        with pytest.raises(PermissionError):
            atomic_json(target, {"version": 2})
    assert time.monotonic() - began < 4.5
    assert json.loads(target.read_bytes()) == {"version": 1}
    assert not list(tmp_path.glob("*.tmp"))
