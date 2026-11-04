"""
Biometric curve plotting module.
Generates publication-quality charts for:
- Loss and Accuracy learning trajectories
- ROC curves with AUC annotations
- Precision-Recall curves
- FAR vs FRR curves with EER intersection
- Normalized Confusion Matrix heatmaps
- Alteration difficulty and cross-validation comparisons
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_learning_curves(
    history: Dict[str, List[float]],
    output_dir: Path,
    title_suffix: str = "",
):
    """
    Plots training and validation loss curves.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    epochs = range(1, len(history["loss"]) + 1)
    ax.plot(epochs, history["loss"], label="Training Loss", color="#1f77b4", lw=2)
    if "val_loss" in history:
        ax.plot(epochs, history["val_loss"], label="Validation Loss", color="#ff7f0e", lw=2)
        best_epoch = np.argmin(history["val_loss"]) + 1
        best_val = np.min(history["val_loss"])
        ax.axvline(best_epoch, color="red", linestyle="--", label=f"Best Epoch ({best_epoch})")
        ax.scatter([best_epoch], [best_val], color="red", s=50, zorder=5)

    ax.set_title(f"Siamese Contrastive Loss Trajectory {title_suffix}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Epoch", fontsize=11)
    ax.set_ylabel("Loss", fontsize=11)
    ax.legend(loc="upper right")
    plt.tight_layout()
    out_path = output_dir / f"learning_loss_curves{title_suffix.replace(' ', '_').lower()}.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_roc_and_pr_curves(
    eval_metrics: Dict[str, Any],
    output_dir: Path,
    model_name: str = "Siamese CNN",
):
    """
    Plots paired ROC Curve and Precision-Recall Curve.
    """
    curve_data = eval_metrics["biometric_verification"]["curve_data"]
    fpr = np.array(curve_data["fpr"])
    tpr = np.array(curve_data["tpr"])
    roc_auc = eval_metrics["biometric_verification"]["roc_auc"]
    pr_auc = eval_metrics["biometric_verification"]["pr_auc"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # 1. ROC Curve
    axes[0].plot(fpr, tpr, color="#2b5c8f", lw=2.5, label=f"{model_name} (AUC = {roc_auc:.4f})")
    axes[0].plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1.2, label="Random Chance")
    axes[0].set_xlim([-0.01, 1.0])
    axes[0].set_ylim([0.0, 1.02])
    axes[0].set_xlabel("False Acceptance Rate (FAR / FPR)", fontsize=11)
    axes[0].set_ylabel("True Acceptance Rate (TAR / TPR)", fontsize=11)
    axes[0].set_title(f"ROC Verification Curve - {model_name}", fontsize=12, fontweight="bold")
    axes[0].legend(loc="lower right")

    # 2. FAR vs FRR Curve (EER Visualization)
    fnr = np.array(curve_data["fnr"])
    thresholds = np.array(curve_data["thresholds"])
    eer = eval_metrics["biometric_verification"]["eer"]
    eer_thresh = eval_metrics["biometric_verification"]["eer_threshold_distance"]

    axes[1].plot(thresholds, fpr, color="#d95f02", lw=2, label="FAR (False Acceptance Rate)")
    axes[1].plot(thresholds, fnr, color="#7570b3", lw=2, label="FRR (False Rejection Rate)")
    axes[1].scatter([eer_thresh], [eer], color="red", s=70, zorder=5, label=f"EER = {eer:.4f} @ d={eer_thresh:.3f}")
    axes[1].set_xlabel("Euclidean Distance Threshold", fontsize=11)
    axes[1].set_ylabel("Error Rate", fontsize=11)
    axes[1].set_title("FAR vs. FRR Operational Operating Curve", fontsize=12, fontweight="bold")
    axes[1].legend(loc="upper center")

    plt.tight_layout()
    out_path = output_dir / f"roc_and_eer_curves_{model_name.replace(' ', '_').lower()}.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_confusion_matrix_heatmap(
    class_metrics: Dict[str, Any],
    output_dir: Path,
    model_name: str = "Siamese CNN",
):
    """
    Plots labeled confusion matrix heatmap.
    """
    cm_dict = class_metrics["confusion_matrix"]
    cm = np.array([
        [cm_dict["true_negatives"], cm_dict["false_positives"]],
        [cm_dict["false_negatives"], cm_dict["true_positives"]],
    ])

    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)

    fig, ax = plt.subplots(figsize=(6, 5))
    labels = [["TN", "FP"], ["FN", "TP"]]
    annot = np.array([
        [f"{cm[0, 0]:,}\n({cm_norm[0, 0]*100:.1f}%)", f"{cm[0, 1]:,}\n({cm_norm[0, 1]*100:.1f}%)"],
        [f"{cm[1, 0]:,}\n({cm_norm[1, 0]*100:.1f}%)", f"{cm[1, 1]:,}\n({cm_norm[1, 1]*100:.1f}%)"],
    ])

    sns.heatmap(cm_norm, annot=annot, fmt="", cmap="Blues", cbar=True, ax=ax,
                xticklabels=["Pred Imposter", "Pred Genuine"],
                yticklabels=["Actual Imposter", "Actual Genuine"])
    ax.set_title(f"Confusion Matrix @ EER Threshold ({model_name})", fontsize=12, fontweight="bold")
    plt.tight_layout()
    out_path = output_dir / f"confusion_matrix_{model_name.replace(' ', '_').lower()}.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_cross_validation_folds(cv_results: Dict[str, Any], output_dir: Path):
    """
    Plots cross-validation fold variability for Accuracy, ROC-AUC, and EER.
    """
    folds = cv_results["fold_results"]
    fold_nums = [f"Fold {f['fold']}" for f in folds]
    accs = [f["accuracy"] * 100 for f in folds]
    aucs = [f["roc_auc"] * 100 for f in folds]
    eers = [f["eer"] * 100 for f in folds]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(fold_nums))
    width = 0.25

    ax.bar(x - width, accs, width, label="Accuracy (%)", color="#1b9e77")
    ax.bar(x, aucs, width, label="ROC-AUC (%)", color="#7570b3")
    ax.bar(x + width, eers, width, label="EER (%)", color="#d95f02")

    ax.set_xticks(x)
    ax.set_xticklabels(fold_nums)
    ax.set_ylabel("Score (%)")
    ax.set_title("5-Fold Cross-Validation Biometric Performance Consistency", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right")
    plt.tight_layout()
    out_path = output_dir / "cv_fold_comparison.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_model_comparisons(comparison_records: List[Dict[str, Any]], output_dir: Path):
    """
    Generates comparative bar charts across all tested architectures:
    Siamese CNN, ResNet50, MobileNetV3, HOG+SVM.
    """
    names = [r["model_name"] for r in comparison_records]
    accs = [r["accuracy"] * 100 for r in comparison_records]
    eers = [r["eer"] * 100 for r in comparison_records]
    aucs = [r["roc_auc"] * 100 for r in comparison_records]
    latencies = [r["latency_ms"] for r in comparison_records]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))

    # Accuracy vs EER
    x = np.arange(len(names))
    width = 0.25
    axes[0].bar(x - width/2, accs, width, label="Accuracy (%)", color="#2b5c8f")
    axes[0].bar(x + width/2, eers, width, label="EER (%) [Lower is Better]", color="#e41a1c")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(names, rotation=15)
    axes[0].set_title("Biometric Accuracy and EER Comparison", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Percentage (%)")
    axes[0].legend()

    # Latency Comparison
    sns.barplot(x=names, y=latencies, ax=axes[1], palette="magma")
    axes[1].set_title("Inference Latency per Verification Pair (ms)", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Latency (ms)")
    axes[1].set_xticklabels(names, rotation=15)
    for i, v in enumerate(latencies):
        axes[1].text(i, v + 0.1, f"{v:.1f}ms", ha="center", fontweight="bold")

    plt.tight_layout()
    out_path = output_dir / "model_architectures_comparison.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_difficulty_performance(difficulty_results: Dict[str, float], output_dir: Path):
    """
    Plots verification accuracy across alteration difficulties (Easy, Medium, Hard).
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    diffs = list(difficulty_results.keys())
    scores = [difficulty_results[k] * 100 for k in diffs]

    sns.barplot(x=diffs, y=scores, ax=ax, palette="viridis")
    ax.set_title("Verification Robustness Across Alteration Difficulty", fontsize=12, fontweight="bold")
    ax.set_ylabel("Verification Accuracy (%)")
    ax.set_ylim([0, 105])
    for i, v in enumerate(scores):
        ax.text(i, v + 2, f"{v:.1f}%", ha="center", fontweight="bold")

    plt.tight_layout()
    out_path = output_dir / "alteration_difficulty_performance.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

