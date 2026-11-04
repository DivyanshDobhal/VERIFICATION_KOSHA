"""
High-resolution visualization generator for SOCOFing EDA.
Uses Matplotlib and Seaborn with publication-quality styling.
"""

from pathlib import Path
from typing import Optional
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Configure styling
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
})


def plot_dataset_distributions(df: pd.DataFrame, output_dir: Path):
    """
    Plots dataset distribution charts:
    - Real vs Altered
    - Alteration Category breakdown
    - Difficulty level breakdown
    - Gender distribution
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Real vs Altered
    labels = ["Original (Real)", "Altered"]
    counts = [(~df["is_altered"]).sum(), df["is_altered"].sum()]
    colors = ["#2b5c8f", "#d95f02"]
    axes[0, 0].pie(counts, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140, explode=(0.05, 0))
    axes[0, 0].set_title("Dataset Composition: Original vs Altered")

    # 2. Alteration Categories
    altered_df = df[df["is_altered"]]
    cat_counts = altered_df["alteration_category"].value_counts()
    sns.barplot(x=cat_counts.index, y=cat_counts.values, ax=axes[0, 1], palette="Blues_r")
    axes[0, 1].set_title("Alteration Category Distribution")
    axes[0, 1].set_ylabel("Count")
    axes[0, 1].set_xlabel("Alteration Type")
    for i, v in enumerate(cat_counts.values):
        axes[0, 1].text(i, v + 200, f"{v:,}", ha="center", fontweight="bold")

    # 3. Difficulty Level
    diff_counts = altered_df["difficulty"].value_counts()[["Easy", "Medium", "Hard"]]
    sns.barplot(x=diff_counts.index, y=diff_counts.values, ax=axes[1, 0], palette="crest")
    axes[1, 0].set_title("Altered Fingerprint Difficulty Distribution")
    axes[1, 0].set_ylabel("Count")
    axes[1, 0].set_xlabel("Difficulty Level")
    for i, v in enumerate(diff_counts.values):
        axes[1, 0].text(i, v + 200, f"{v:,}", ha="center", fontweight="bold")

    # 4. Gender Distribution
    gender_counts = df["gender"].value_counts()
    sns.barplot(x=gender_counts.index, y=gender_counts.values, ax=axes[1, 1], palette="flare")
    axes[1, 1].set_title("Subject Gender Distribution (Images)")
    axes[1, 1].set_ylabel("Count")
    axes[1, 1].set_xlabel("Gender")
    for i, v in enumerate(gender_counts.values):
        axes[1, 1].text(i, v + 400, f"{v:,}", ha="center", fontweight="bold")

    plt.tight_layout()
    save_path = output_dir / "eda_dataset_distributions.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_finger_and_subject_distributions(df: pd.DataFrame, output_dir: Path):
    """
    Plots subject image counts and finger distributions.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Subject images distribution
    subj_counts = df.groupby("subject_id").size()
    sns.histplot(subj_counts, kde=True, ax=axes[0], color="#1b9e77", bins=30)
    axes[0].set_title("Distribution of Images per Subject")
    axes[0].set_xlabel("Number of Images")
    axes[0].set_ylabel("Subject Count")
    axes[0].axvline(subj_counts.mean(), color="red", linestyle="--", label=f"Mean: {subj_counts.mean():.1f}")
    axes[0].legend()

    # Finger Distribution across hands
    finger_order = ["thumb", "index", "middle", "ring", "little"]
    sns.countplot(data=df, x="finger", hue="hand", order=finger_order, ax=axes[1], palette="Set2")
    axes[1].set_title("Finger Distribution by Hand (Left vs Right)")
    axes[1].set_xlabel("Finger Type")
    axes[1].set_ylabel("Image Count")

    plt.tight_layout()
    save_path = output_dir / "eda_finger_subject_distributions.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_original_vs_altered_comparison(df: pd.DataFrame, output_dir: Path):
    """
    Finds a finger that has original and all three alterations (CR, Obl, Zcut)
    and plots them side by side.
    """
    # Find a subject and finger with original and all alterations
    altered = df[df["is_altered"]]
    original = df[~df["is_altered"]]

    common_groups = list(set(original["source_finger_group"]).intersection(set(altered["source_finger_group"])))
    if not common_groups:
        return

    sample_group = common_groups[0]
    orig_row = original[original["source_finger_group"] == sample_group].iloc[0]
    alt_rows = altered[altered["source_finger_group"] == sample_group]

    # Select CR, Obl, Zcut if available
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))
    orig_img = cv2.imread(orig_row["file_path"], cv2.IMREAD_GRAYSCALE)
    axes[0].imshow(orig_img, cmap="gray")
    axes[0].set_title(f"Original\n({orig_row['finger_label']})", fontsize=11, fontweight="bold")
    axes[0].axis("off")

    categories = ["Central Rotation", "Obliteration", "Z-cut"]
    for i, cat in enumerate(categories, start=1):
        cat_match = alt_rows[alt_rows["alteration_category"] == cat]
        if not cat_match.empty:
            alt_img = cv2.imread(cat_match.iloc[0]["file_path"], cv2.IMREAD_GRAYSCALE)
            axes[i].imshow(alt_img, cmap="gray")
            axes[i].set_title(f"{cat}\n({cat_match.iloc[0]['difficulty']})", fontsize=11, fontweight="bold")
        else:
            axes[i].text(0.5, 0.5, "N/A", ha="center", va="center")
        axes[i].axis("off")

    plt.suptitle(f"Original vs Alteration Categories (Source: {sample_group})", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_path = output_dir / "eda_original_vs_altered_comparison.png"
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_difficulty_comparisons(df: pd.DataFrame, output_dir: Path):
    """
    Plots comparison across Easy, Medium, and Hard difficulty levels.
    """
    altered = df[df["is_altered"]]
    groups_with_all_diff = []
    for grp, grp_df in altered.groupby("source_finger_group"):
        diffs = set(grp_df["difficulty"])
        if {"Easy", "Medium", "Hard"}.issubset(diffs):
            groups_with_all_diff.append(grp)
            if len(groups_with_all_diff) >= 3:
                break

    if not groups_with_all_diff:
        return

    fig, axes = plt.subplots(len(groups_with_all_diff), 4, figsize=(14, 3.5 * len(groups_with_all_diff)))
    if len(groups_with_all_diff) == 1:
        axes = np.expand_dims(axes, 0)

    for r, grp in enumerate(groups_with_all_diff):
        orig_row = df[(df["source_finger_group"] == grp) & (~df["is_altered"])]
        if not orig_row.empty:
            img = cv2.imread(orig_row.iloc[0]["file_path"], cv2.IMREAD_GRAYSCALE)
            axes[r, 0].imshow(img, cmap="gray")
            axes[r, 0].set_title(f"Original\n({grp})")
        axes[r, 0].axis("off")

        for c, diff in enumerate(["Easy", "Medium", "Hard"], start=1):
            diff_row = altered[(altered["source_finger_group"] == grp) & (altered["difficulty"] == diff)]
            if not diff_row.empty:
                img = cv2.imread(diff_row.iloc[0]["file_path"], cv2.IMREAD_GRAYSCALE)
                axes[r, c].imshow(img, cmap="gray")
                axes[r, c].set_title(f"{diff}\n({diff_row.iloc[0]['alteration_category']})")
            axes[r, c].axis("off")

    plt.suptitle("Fingerprint Comparison Across Alteration Difficulty Levels", fontsize=14, fontweight="bold")
    plt.tight_layout()
    save_path = output_dir / "eda_difficulty_comparisons.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_random_samples_gallery(df: pd.DataFrame, output_dir: Path, n_samples: int = 12):
    """
    Plots a grid of random fingerprint samples showing diverse subjects and fingers.
    """
    sample_df = df.sample(n=n_samples, random_state=42)
    cols = 4
    rows = (n_samples + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
    axes = axes.flatten()

    for idx, (_, row) in enumerate(sample_df.iterrows()):
        img = cv2.imread(row["file_path"], cv2.IMREAD_GRAYSCALE)
        axes[idx].imshow(img, cmap="gray")
        alt_str = f"Alt: {row['alteration_code']} ({row['difficulty']})" if row["is_altered"] else "Original"
        axes[idx].set_title(f"Subj {row['subject_id']} | {row['finger_label']}\n{alt_str}", fontsize=9)
        axes[idx].axis("off")

    for idx in range(len(sample_df), len(axes)):
        axes[idx].axis("off")

    plt.suptitle("SOCOFing Random Fingerprint Dataset Samples", fontsize=14, fontweight="bold")
    plt.tight_layout()
    save_path = output_dir / "eda_random_samples_gallery.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")

