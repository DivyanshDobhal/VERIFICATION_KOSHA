"""
End-to-end integration test client for KOSHA LABS Biometric API.
Tests:
1. Health check & configuration
2. Worker enrollment with biometric image
3. Duplicate worker registration prevention (blocking duplicate biometric enrollments)
4. Multi-session recording appending for permanent Worker ID
5. 1:1 Biometric Verification (Worker ID verification & Image-to-Image verification)
6. 1:N Biometric Identification (Probe searching gallery)
7. Numerical 128-D embedding extraction
8. Worker gallery listing
"""

import tensorflow as tf
import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.service.api import app, gallery
from config.settings import REPORTS_DIR


def main():
    print("=" * 70)
    print("INTEGRATION TEST: KOSHA LABS Biometric Fingerprint REST API")
    print("=" * 70)

    # Reset gallery store for pristine test run
    gallery.workers.clear()
    gallery.save()

    metadata_path = REPORTS_DIR / "socofing_parsed_metadata.csv"
    if not metadata_path.exists():
        print(f"Metadata file {metadata_path} not found.")
        sys.exit(1)

    df = pd.read_csv(metadata_path)

    # Pick 2 different subjects for test cases
    subjs = df["subject_id"].unique()
    subj1 = subjs[0]
    subj2 = subjs[1]

    # Alice's primary finger (multiple impressions)
    alice_fgs = df[df["subject_id"] == subj1]["source_finger_group"].unique()
    alice_primary_fg = alice_fgs[0]
    alice_primary_imgs = df[df["source_finger_group"] == alice_primary_fg]["file_path"].tolist()

    img1_sess1 = alice_primary_imgs[0]
    img1_probe = alice_primary_imgs[1] if len(alice_primary_imgs) > 1 else alice_primary_imgs[0]

    # Alice's secondary finger for multi-session enrollment
    alice_sec_fg = alice_fgs[1] if len(alice_fgs) > 1 else alice_primary_fg
    alice_sec_imgs = df[df["source_finger_group"] == alice_sec_fg]["file_path"].tolist()
    img1_sess2 = alice_sec_imgs[0]

    # Bob's finger (imposter)
    subj2_imgs = df[df["subject_id"] == subj2]["file_path"].tolist()
    img2_sess1 = subj2_imgs[0]

    client = TestClient(app)

    # 1. Health check
    print("\n1. Testing GET /health...")
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.text}"
    health_data = resp.json()
    print(f"   Response: Status={health_data['status']}, Architecture={health_data['model_architecture']}")

    # 2. Enroll Worker 1 (Alice)
    print(f"\n2. Testing POST /enroll for Worker 'WRK-1001' (Subj {subj1})...")
    with open(img1_sess1, "rb") as f:
        resp = client.post(
            "/enroll",
            data={
                "worker_id": "WRK-1001",
                "name": "Alice Montgomery",
                "department": "Biometric Research",
                "finger_label": "Right_index_finger",
            },
            files={"fingerprint_image": ("finger1.bmp", f, "image/bmp")},
        )
    assert resp.status_code == 201, f"Enrollment failed: {resp.text}"
    enroll_data = resp.json()
    print(f"   Success: Worker enrolled -> ID={enroll_data['worker_id']}, Session={enroll_data['session_id']}")

    # 3. Duplicate Prevention Test: Try enrolling Worker 2 with the SAME fingerprint biometric
    print("\n3. Testing Duplicate Prevention: Attempting to enroll 'WRK-9999' with Alice's fingerprint...")
    with open(img1_sess1, "rb") as f:
        resp = client.post(
            "/enroll",
            data={
                "worker_id": "WRK-9999",
                "name": "Imposter Registration",
                "department": "Security Breach Attempt",
                "finger_label": "Right_index_finger",
            },
            files={"fingerprint_image": ("finger1_duplicate.bmp", f, "image/bmp")},
        )
    print(f"   Response Code: {resp.status_code} (Expected: 409 Conflict)")
    assert resp.status_code == 409, f"Duplicate prevention failed to block! Response: {resp.text}"
    dup_data = resp.json()
    print(f"   Duplicate Prevention Verified! Block Message: {dup_data['message']}")

    # 4. Multi-session Recording: Add session 2 to Worker 1 (Alice)
    print("\n4. Testing POST /sessions: Adding 2nd fingerprint recording to Worker 'WRK-1001'...")
    with open(img1_sess2, "rb") as f:
        resp = client.post(
            "/sessions",
            data={
                "worker_id": "WRK-1001",
                "finger_label": "Right_thumb_finger",
                "notes": "Annual Recertification Scan",
            },
            files={"fingerprint_image": ("finger2.bmp", f, "image/bmp")},
        )
    assert resp.status_code == 200, f"Adding session failed: {resp.text}"
    sess_data = resp.json()
    print(f"   Success: Session added -> Total Sessions for WRK-1001 = {sess_data['total_sessions']}")

    # 5. Enroll Worker 2 (Bob) with different genuine fingerprint
    print(f"\n5. Testing POST /enroll for Worker 'WRK-1002' (Subj {subj2})...")
    with open(img2_sess1, "rb") as f:
        resp = client.post(
            "/enroll",
            data={
                "worker_id": "WRK-1002",
                "name": "Bob Jenkins",
                "department": "Engineering Operations",
                "finger_label": "Left_middle_finger",
            },
            files={"fingerprint_image": ("finger_bob.bmp", f, "image/bmp")},
        )
    assert resp.status_code == 201, f"Enrollment of Worker 2 failed: {resp.text}"
    print(f"   Success: Worker 2 enrolled -> ID={resp.json()['worker_id']}")

    # 6. 1:1 Verification: Verify Alice probe against WRK-1001
    print("\n6. Testing POST /verify (1:1 Worker Verification)...")
    with open(img1_probe, "rb") as f:
        resp = client.post(
            "/verify",
            data={"worker_id": "WRK-1001", "security_level": "standard"},
            files={"fingerprint_image": ("probe.bmp", f, "image/bmp")},
        )
    assert resp.status_code == 200, f"Verification request failed: {resp.text}"
    verif_data = resp.json()
    print(f"   Genuine Match Result: Verified={verif_data['verified']}, Distance={verif_data['distance']:.4f}, Confidence={verif_data['confidence_score']*100:.1f}%")
    assert verif_data["verified"] is True, f"Genuine match was falsely rejected! Distance: {verif_data['distance']}, Threshold: {verif_data['threshold']}"

    # Imposter test: Verify Bob's fingerprint against Alice's ID (WRK-1001)
    with open(img2_sess1, "rb") as f:
        resp = client.post(
            "/verify",
            data={"worker_id": "WRK-1001", "security_level": "standard"},
            files={"fingerprint_image": ("bob_probe.bmp", f, "image/bmp")},
        )
    imposter_data = resp.json()
    print(f"   Imposter Mismatch Result: Verified={imposter_data['verified']}, Distance={imposter_data['distance']:.4f}, Decision={imposter_data['decision']}")
    assert imposter_data["verified"] is False, "Imposter was falsely accepted!"

    # 7. 1:1 Image-to-Image Verification
    print("\n7. Testing POST /verify (1:1 Image-to-Image Direct Verification)...")
    with open(img1_sess1, "rb") as f1, open(img1_probe, "rb") as f2:
        resp = client.post(
            "/verify",
            data={"security_level": "standard"},
            files={
                "fingerprint_image": ("imgA.bmp", f1, "image/bmp"),
                "secondary_image": ("imgB.bmp", f2, "image/bmp"),
            },
        )
    assert resp.status_code == 200
    img2img = resp.json()
    print(f"   Image-to-Image Result: Verified={img2img['verified']}, Distance={img2img['euclidean_distance']:.4f}, Decision={img2img['decision']}")
    assert img2img["verified"] is True, f"Image-to-image genuine match falsely rejected! Distance: {img2img['euclidean_distance']}"

    # 8. 1:N Biometric Identification
    print("\n8. Testing POST /identify (1:N Gallery Search)...")
    with open(img1_probe, "rb") as f:
        resp = client.post(
            "/identify",
            params={"top_k": 5},
            files={"fingerprint_image": ("probe.bmp", f, "image/bmp")},
        )
    assert resp.status_code == 200
    ident_res = resp.json()
    print(f"   1:N Search Identified={ident_res['identified']}")
    if ident_res['rank_1_match']:
        print(f"   Rank-1 Match: Worker ID={ident_res['rank_1_match']['worker_id']}, Name={ident_res['rank_1_match']['name']}, Distance={ident_res['rank_1_match']['distance']:.4f}")

    # 9. Numerical Embedding Extraction
    print("\n9. Testing POST /embeddings (128-D Numerical Vector Generation)...")
    with open(img1_sess1, "rb") as f:
        resp = client.post(
            "/embeddings",
            files={"fingerprint_image": ("sample.bmp", f, "image/bmp")},
        )
    assert resp.status_code == 200
    emb_data = resp.json()
    print(f"   Embedding Vector Extracted: Dimension={emb_data['embedding_dimension']}, L2 Norm={emb_data['l2_norm']:.4f}")
    assert emb_data["embedding_dimension"] == 128
    assert abs(emb_data["l2_norm"] - 1.0) < 1e-4

    # 10. List Gallery Workers
    print("\n10. Testing GET /workers...")
    resp = client.get("/workers")
    assert resp.status_code == 200
    workers_list = resp.json()
    print(f"   Total Enrolled Workers: {workers_list['total_workers']}")
    for w in workers_list["workers"]:
        print(f"     - ID: {w['worker_id']} | Name: {w['name']} | Sessions: {w['total_sessions']} | Fingers: {w['enrolled_fingers']}")

    print("\n" + "=" * 70)
    print("ALL API INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
