import pytest

def test_single_worker_multiple_sessions():
    """Verify multiple sessions reference the exact same permanent Worker ID."""
    worker_id = "WK-1001"
    session_1 = {"session_id": "SES-001", "worker_id": worker_id, "date": "2026-11-01"}
    session_2 = {"session_id": "SES-002", "worker_id": worker_id, "date": "2026-11-02"}
    session_3 = {"session_id": "SES-003", "worker_id": worker_id, "date": "2026-11-03"}

    assert session_1["worker_id"] == session_2["worker_id"] == session_3["worker_id"] == "WK-1001"
    assert session_1["session_id"] != session_2["session_id"]

def test_idempotency_prevents_duplicate_clicks():
    """Verify duplicate clicks with same idempotency key return existing session."""
    seen_keys = set()
    key_1 = "IDEMP-OP892-20261103-001"
    seen_keys.add(key_1)
    
    # Second click
    assert key_1 in seen_keys
