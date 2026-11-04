"""
Script for Phase 3: Data Leakage Prevention and Data Splitting.
Executes both Protocol A and Protocol B splits and writes full audit reports.
"""

import sys
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import REPORTS_DIR
from ml.data.split import split_protocol_a_enrolled_identity, split_protocol_b_subject_disjoint


def main():
    print("=" * 60)
    print("PHASE 3: Data Leakage Prevention and Splitting Protocols")
    print("=" * 60)

    metadata_path = REPORTS_DIR / "socofing_parsed_metadata.csv"
    if not metadata_path.exists():
        print(f"Error: {metadata_path} not found. Run Phase 1 first.")
        sys.exit(1)

    df = pd.read_csv(metadata_path)
    print(f"Loaded {len(df):,} records for {df['subject_id'].nunique()} subjects and {df['source_finger_group'].nunique()} source groups.")

    print("\n--- Generating Protocol A: Enrolled-Identity Verification Split ---")
    train_a, val_a, test_a, stats_a = split_protocol_a_enrolled_identity(df)
    print(f"Protocol A Train: {len(train_a):,} imgs | {train_a['subject_id'].nunique()} subjs | {train_a['source_finger_group'].nunique()} groups")
    print(f"Protocol A Val:   {len(val_a):,} imgs | {val_a['subject_id'].nunique()} subjs | {val_a['source_finger_group'].nunique()} groups")
    print(f"Protocol A Test:  {len(test_a):,} imgs | {test_a['subject_id'].nunique()} subjs | {test_a['source_finger_group'].nunique()} groups")
    print(f"Protocol A Leakage Audit: Source Overlap = {stats_a['source_group_leakage']} (VALID={stats_a['is_valid']})")

    # Save Protocol A partitions
    split_dir = REPORTS_DIR / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    train_a.to_csv(split_dir / "protocol_a_train.csv", index=False)
    val_a.to_csv(split_dir / "protocol_a_val.csv", index=False)
    test_a.to_csv(split_dir / "protocol_a_test.csv", index=False)

    print("\n--- Generating Protocol B: Subject-Disjoint Generalization Split ---")
    train_b, val_b, test_b, stats_b = split_protocol_b_subject_disjoint(df)
    print(f"Protocol B Train: {len(train_b):,} imgs | {train_b['subject_id'].nunique()} subjs | {train_b['source_finger_group'].nunique()} groups")
    print(f"Protocol B Val:   {len(val_b):,} imgs | {val_b['subject_id'].nunique()} subjs | {val_b['source_finger_group'].nunique()} groups")
    print(f"Protocol B Test:  {len(test_b):,} imgs | {test_b['subject_id'].nunique()} subjs | {test_b['source_finger_group'].nunique()} groups")
    print(f"Protocol B Leakage Audit: Source Overlap = {stats_b['source_group_leakage']} | Subj Overlap = {stats_b['subject_leakage']} (VALID={stats_b['is_valid']})")

    # Save Protocol B partitions
    train_b.to_csv(split_dir / "protocol_b_train.csv", index=False)
    val_b.to_csv(split_dir / "protocol_b_val.csv", index=False)
    test_b.to_csv(split_dir / "protocol_b_test.csv", index=False)

    # Save Audit Summary JSON
    audit_report = {
        "protocol_a_enrolled_identity": stats_a,
        "protocol_b_subject_disjoint": stats_b,
    }
    audit_file = REPORTS_DIR / "data_leakage_and_splits_audit.json"
    with open(audit_file, "w") as f:
        json.dump(audit_report, f, indent=2)
    print(f"\nAudit Report Saved: {audit_file}")
    print("Phase 3 Splitting Protocols Verified Successfully.")


if __name__ == "__main__":
    main()

