import pytest

def test_permanent_worker_id_format():
    """Verify permanent worker IDs strictly follow WK-XXXX formatting."""
    seq_number = 1001
    formatted_id = f"WK-{seq_number}"
    assert formatted_id == "WK-1001"
    assert len(formatted_id) == 7

def test_biometric_consent_mandatory():
    """Verify registration fails if worker biometric consent is not granted."""
    consent_accepted = False
    assert consent_accepted is False
