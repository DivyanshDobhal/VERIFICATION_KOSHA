"""
Data leakage prevention and rigorous partitioning module.
Implements:
1. Protocol A: Enrolled-Identity Verification (Subject overlap, disjoint source fingerprint groups).
2. Protocol B: Subject-Disjoint Generalization (Strictly disjoint subjects and source groups).
"""

from typing import Tuple, Dict, Any, List
import numpy as np
import pandas as pd


def verify_partition_integrity(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    protocol_name: str,
) -> Dict[str, Any]:
    """
    Validates that there is zero source-group data leakage across partitions.
    For Protocol B, also validates zero subject leakage.
    """
    train_groups = set(train_df["source_finger_group"])
    val_groups = set(val_df["source_finger_group"])
    test_groups = set(test_df["source_finger_group"])

    leakage_train_val = train_groups.intersection(val_groups)
    leakage_train_test = train_groups.intersection(test_groups)
    leakage_val_test = val_groups.intersection(test_groups)

    train_subjects = set(train_df["subject_id"])
    val_subjects = set(val_df["subject_id"])
    test_subjects = set(test_df["subject_id"])

    subj_leak_train_val = train_subjects.intersection(val_subjects)
    subj_leak_train_test = train_subjects.intersection(test_subjects)
    subj_leak_val_test = val_subjects.intersection(test_subjects)

    is_source_leak_free = (
        len(leakage_train_val) == 0
        and len(leakage_train_test) == 0
        and len(leakage_val_test) == 0
    )

    if protocol_name == "Protocol B (Subject-Disjoint)":
        is_subject_leak_free = (
            len(subj_leak_train_val) == 0
            and len(subj_leak_train_test) == 0
            and len(subj_leak_val_test) == 0
        )
    else:
        # Protocol A allows subject overlap, but enforces source group disjointness
        is_subject_leak_free = True

    stats = {
        "protocol": protocol_name,
        "train_images": len(train_df),
        "val_images": len(val_df),
        "test_images": len(test_df),
        "train_subjects": len(train_subjects),
        "val_subjects": len(val_subjects),
        "test_subjects": len(test_subjects),
        "train_source_groups": len(train_groups),
        "val_source_groups": len(val_groups),
        "test_source_groups": len(test_groups),
        "source_group_leakage": {
            "train_val_overlap": len(leakage_train_val),
            "train_test_overlap": len(leakage_train_test),
            "val_test_overlap": len(leakage_val_test),
        },
        "subject_leakage": {
            "train_val_overlap": len(subj_leak_train_val),
            "train_test_overlap": len(subj_leak_train_test),
            "val_test_overlap": len(subj_leak_val_test),
        },
        "is_valid": is_source_leak_free and is_subject_leak_free,
    }

    if not is_source_leak_free:
        raise ValueError(f"FATAL: Source fingerprint group leakage detected in {protocol_name}!")
    if protocol_name == "Protocol B (Subject-Disjoint)" and not is_subject_leak_free:
        raise ValueError(f"FATAL: Subject ID leakage detected in {protocol_name}!")

    return stats


def split_protocol_a_enrolled_identity(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Protocol A: Enrolled-Identity Verification
    - Each subject's finger source groups are partitioned across train, val, and test.
    - All alterations belonging to a source group remain strictly inside its partition.
    - Allows evaluating recognition of enrolled identities on unseen captures/finger groups.
    """
    rng = np.random.RandomState(seed)
    train_groups = []
    val_groups = []
    test_groups = []

    # Partition source groups per subject
    for subj_id, subj_df in df.groupby("subject_id"):
        groups = list(subj_df["source_finger_group"].unique())
        rng.shuffle(groups)
        n = len(groups)
        n_train = max(1, int(round(n * train_ratio)))
        n_val = max(1, int(round(n * val_ratio)))
        if n_train + n_val >= n:
            n_val = max(1, n - n_train - 1)

        t_grp = groups[:n_train]
        v_grp = groups[n_train : n_train + n_val]
        te_grp = groups[n_train + n_val :]

        train_groups.extend(t_grp)
        val_groups.extend(v_grp)
        test_groups.extend(te_grp)

    train_df = df[df["source_finger_group"].isin(train_groups)].copy()
    val_df = df[df["source_finger_group"].isin(val_groups)].copy()
    test_df = df[df["source_finger_group"].isin(test_groups)].copy()

    stats = verify_partition_integrity(
        train_df, val_df, test_df, "Protocol A (Enrolled-Identity)"
    )
    return train_df, val_df, test_df, stats


def split_protocol_b_subject_disjoint(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Protocol B: Subject-Disjoint Generalization
    - Unique subjects are partitioned into strictly disjoint sets.
    - Zero subjects or source groups overlap across train, val, and test.
    - Evaluates generalizable biometric feature representation on unseen individuals.
    """
    rng = np.random.RandomState(seed)
    subjects = np.array(df["subject_id"].unique())
    rng.shuffle(subjects)

    n_subj = len(subjects)
    n_train = int(round(n_subj * train_ratio))
    n_val = int(round(n_subj * val_ratio))

    train_subjs = set(subjects[:n_train])
    val_subjs = set(subjects[n_train : n_train + n_val])
    test_subjs = set(subjects[n_train + n_val :])

    train_df = df[df["subject_id"].isin(train_subjs)].copy()
    val_df = df[df["subject_id"].isin(val_subjs)].copy()
    test_df = df[df["subject_id"].isin(test_subjs)].copy()

    stats = verify_partition_integrity(
        train_df, val_df, test_df, "Protocol B (Subject-Disjoint)"
    )
    return train_df, val_df, test_df, stats

