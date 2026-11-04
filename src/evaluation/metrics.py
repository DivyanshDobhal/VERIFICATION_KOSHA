"""
Comprehensive biometric evaluation metrics engine for KOSHA LABS.
Calculates:
1. Standard Classification Metrics (Accuracy, Precision, Recall, F1, Specificity, MCC, Kappa, Confusion Matrix)
2. Biometric Verification Metrics (FAR, FRR, EER, GAR, ROC-AUC, PR-AUC, TAR @ FAR=0.1%, TAR @ FAR=1%, TAR @ FAR=5%)
3. Biometric Identification Metrics (Rank-1, Rank-5, Top-K, Mean Reciprocal Rank)
4. System & Model Performance Metrics (Inference latency, throughput, model size, parameter count)
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import scipy.interpolate
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    matthews_corrcoef,
    cohen_kappa_score,
    balanced_accuracy_score,
    roc_curve,
    auc,
    precision_recall_curve,
)


def compute_classification_metrics(
    y_true: np.ndarray,
    distances: np.ndarray,
    threshold: float,
) -> Dict[str, Any]:
    """
    Computes classification metrics given binary true labels (1=Genuine, 0=Imposter)
    and distance predictions (pair predicted Genuine if distance <= threshold).
    """
    y_pred = (distances <= threshold).astype(int)
    y_true_int = y_true.astype(int)

    cm = confusion_matrix(y_true_int, y_pred, labels=[0, 1])
    # cm layout: [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = cm.ravel()

    acc = float(accuracy_score(y_true_int, y_pred))
    prec = float(precision_score(y_true_int, y_pred, zero_division=0))
    rec = float(recall_score(y_true_int, y_pred, zero_division=0))
    f1 = float(f1_score(y_true_int, y_pred, zero_division=0))
    bal_acc = float(balanced_accuracy_score(y_true_int, y_pred))
    mcc = float(matthews_corrcoef(y_true_int, y_pred))
    kappa = float(cohen_kappa_score(y_true_int, y_pred))

    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    sensitivity = rec  # Sensitivity is identical to Recall / True Positive Rate

    return {
        "threshold": float(threshold),
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "f1_score": f1,
        "balanced_accuracy": bal_acc,
        "matthews_corrcoef": mcc,
        "cohen_kappa": kappa,
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
    }


def compute_biometric_verification_metrics(
    y_true: np.ndarray,
    distances: np.ndarray,
) -> Dict[str, Any]:
    """
    Computes full biometric verification curve metrics:
    - ROC-AUC and PR-AUC
    - EER (Equal Error Rate) and optimal EER threshold
    - FAR, FRR, GAR
    - TAR at FAR = 0.1%, 1.0%, 5.0%
    """
    y_true_int = y_true.astype(int)

    # Convert distances to similarity scores for standard ROC curve calculation:
    # similarity = -distance (or max_dist - distance)
    scores = -distances

    # Compute ROC Curve
    fpr, tpr, roc_thresholds = roc_curve(y_true_int, scores)
    roc_auc = float(auc(fpr, tpr))

    # Compute Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_true_int, scores)
    pr_auc = float(auc(recall, precision))

    # FAR = fpr; FRR = 1 - tpr
    fnr = 1.0 - tpr

    # Equal Error Rate (EER): point where FPR == FNR
    # Find index where abs(FPR - FNR) is minimized
    diff = np.abs(fpr - fnr)
    eer_idx = np.argmin(diff)
    eer = float((fpr[eer_idx] + fnr[eer_idx]) / 2.0)
    eer_threshold_dist = float(-roc_thresholds[eer_idx])  # convert back from score to distance

    # TAR at specific operational FAR thresholds
    def get_tar_at_far(target_far: float) -> float:
        # Interpolate TPR at target FPR
        idx = np.where(fpr <= target_far)[0]
        if len(idx) == 0:
            return 0.0
        return float(tpr[idx[-1]])

    tar_at_far_01 = get_tar_at_far(0.001)  # 0.1%
    tar_at_far_1 = get_tar_at_far(0.01)    # 1.0%
    tar_at_far_5 = get_tar_at_far(0.05)    # 5.0%

    gar = float(1.0 - eer)  # Genuine Acceptance Rate at EER

    # Sample points along ROC and FAR vs FRR curves for visualization
    sample_indices = np.linspace(0, len(fpr) - 1, min(500, len(fpr)), dtype=int)

    return {
        "eer": eer,
        "eer_threshold_distance": eer_threshold_dist,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "gar_at_eer": gar,
        "tar_at_far_0_1_percent": tar_at_far_01,
        "tar_at_far_1_percent": tar_at_far_1,
        "tar_at_far_5_percent": tar_at_far_5,
        "curve_data": {
            "fpr": fpr[sample_indices].tolist(),
            "tpr": tpr[sample_indices].tolist(),
            "fnr": fnr[sample_indices].tolist(),
            "thresholds": (-roc_thresholds[sample_indices]).tolist(),
        },
    }


def compute_identification_metrics(
    gallery_embeddings: np.ndarray,
    gallery_identities: List[Any],
    probe_embeddings: np.ndarray,
    probe_identities: List[Any],
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Computes 1:N Biometric Identification Metrics:
    - Rank-1 Accuracy
    - Rank-5 Accuracy
    - Top-K Accuracy
    - Mean Reciprocal Rank (MRR)
    """
    num_probes = len(probe_identities)
    if num_probes == 0 or len(gallery_identities) == 0:
        return {
            "rank_1_accuracy": 0.0,
            "rank_5_accuracy": 0.0,
            "top_k_accuracy": 0.0,
            "mean_reciprocal_rank": 0.0,
        }

    # Normalize embeddings to ensure cosine similarity equals dot product
    gallery_norm = gallery_embeddings / (np.linalg.norm(gallery_embeddings, axis=1, keepdims=True) + 1e-7)
    probe_norm = probe_embeddings / (np.linalg.norm(probe_embeddings, axis=1, keepdims=True) + 1e-7)

    # Compute cosine similarity matrix: (num_probes, num_gallery)
    sim_matrix = np.dot(probe_norm, gallery_norm.T)

    rank_1_hits = 0
    rank_5_hits = 0
    top_k_hits = 0
    reciprocal_ranks = []

    for i in range(num_probes):
        true_id = probe_identities[i]
        sims = sim_matrix[i]
        # Rank gallery items in descending order of similarity
        sorted_indices = np.argsort(-sims)
        sorted_gallery_ids = [gallery_identities[idx] for idx in sorted_indices]

        # Check hits
        if sorted_gallery_ids[0] == true_id:
            rank_1_hits += 1

        if true_id in sorted_gallery_ids[:5]:
            rank_5_hits += 1

        if true_id in sorted_gallery_ids[:top_k]:
            top_k_hits += 1

        # Reciprocal rank
        try:
            rank_pos = sorted_gallery_ids.index(true_id) + 1
            reciprocal_ranks.append(1.0 / rank_pos)
        except ValueError:
            reciprocal_ranks.append(0.0)

    return {
        "num_probes_evaluated": num_probes,
        "gallery_size": len(gallery_identities),
        "rank_1_accuracy": float(rank_1_hits / num_probes),
        "rank_5_accuracy": float(rank_5_hits / num_probes),
        f"rank_{top_k}_accuracy": float(top_k_hits / num_probes),
        "mean_reciprocal_rank": float(np.mean(reciprocal_ranks)),
    }

