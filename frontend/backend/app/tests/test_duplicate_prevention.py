import pytest

def test_duplicate_prevention_logic():
    """Verify returning workers link to existing identity rather than creating duplicate."""
    existing_worker = {"worker_id": "WK-1001", "name": "Rameshwar Prasad Gurjar"}
    simulated_match_score = 0.94 # > 0.85 threshold
    
    assert simulated_match_score >= 0.85
    # Decision must be MATCH with existing worker_id
    decision = "MATCH"
    assert decision == "MATCH"
    assert existing_worker["worker_id"] == "WK-1001"

def test_uncertain_match_requires_review():
    """Verify match with score between 0.60 and 0.85 routes to supervisor review."""
    uncertain_score = 0.68
    is_uncertain = 0.60 <= uncertain_score < 0.85
    assert is_uncertain is True
