"""
Exploratory Data Analysis (EDA) engine for SOCOFing fingerprint dataset.
Calculates statistical distributions, image quality metrics, corruption checks, and missing data reports.
"""

from pathlib import Path
from typing import Dict, Any
import json
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm


def compute_image_quality_metrics(img_path: str) -> Dict[str, float]:
    """
    Computes biometric image quality indicators:
    - Laplacian variance (focus/sharpness indicator)
    - Mean intensity
    - Standard deviation (contrast indicator)
    - Shannon entropy (information content)
    """
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {
            "is_corrupt": 1.0,
            "height": 0.0,
            "width": 0.0,
            "sharpness": 0.0,
            "mean_intensity": 0.0,
            "std_intensity": 0.0,
            "entropy": 0.0,
        }

    h, w = img.shape
    laplacian_var = float(cv2.Laplacian(img, cv2.CV_64F).var())
    mean_val = float(np.mean(img))
    std_val = float(np.std(img))

    # Shannon Entropy
    hist, _ = np.histogram(img.ravel(), bins=256, range=(0, 256), density=True)
    hist = hist[hist > 0]
    entropy_val = float(-np.sum(hist * np.log2(hist)))

    return {
        "is_corrupt": 0.0,
        "height": float(h),
        "width": float(w),
        "sharpness": laplacian_var,
        "mean_intensity": mean_val,
        "std_intensity": std_val,
        "entropy": entropy_val,
    }


def perform_eda(df: pd.DataFrame, sample_quality_size: int = 1500) -> Dict[str, Any]:
    """
    Performs full exploratory data analysis on the parsed DataFrame.
    """
    total_images = len(df)
    unique_subjects = int(df["subject_id"].nunique())
    unique_source_groups = int(df["source_finger_group"].nunique())

    original_df = df[~df["is_altered"]]
    altered_df = df[df["is_altered"]]

    num_original = len(original_df)
    num_altered = len(altered_df)

    # Subject distribution stats
    images_per_subject = df.groupby("subject_id").size()
    subject_stats = {
        "min": int(images_per_subject.min()),
        "max": int(images_per_subject.max()),
        "mean": float(images_per_subject.mean()),
        "std": float(images_per_subject.std()),
        "median": float(images_per_subject.median()),
    }

    # Finger distribution
    finger_counts = df["finger_label"].value_counts().to_dict()
    finger_category_counts = df["finger"].value_counts().to_dict()
    hand_counts = df["hand"].value_counts().to_dict()
    gender_counts = df["gender"].value_counts().to_dict()

    # Alteration distribution
    alt_category_counts = altered_df["alteration_category"].value_counts().to_dict()
    difficulty_counts = altered_df["difficulty"].value_counts().to_dict()

    # Missing image analysis: Each subject has 10 fingers. Expected original: 10 per subject.
    expected_original_count = unique_subjects * 10
    missing_original_count = max(0, expected_original_count - num_original)

    # Image dimension and quality analysis on a representative sample
    print(f"Sampling {sample_quality_size} images for corruption and quality profiling...")
    sample_df = df.sample(n=min(sample_quality_size, len(df)), random_state=42)

    quality_results = []
    corrupted_files = []

    for _, row in tqdm(sample_df.iterrows(), total=len(sample_df), desc="Quality Analysis"):
        q = compute_image_quality_metrics(row["file_path"])
        if q["is_corrupt"] == 1.0:
            corrupted_files.append(row["file_path"])
        else:
            q["difficulty"] = row["difficulty"]
            q["is_altered"] = row["is_altered"]
            quality_results.append(q)

    q_df = pd.DataFrame(quality_results)

    dimension_stats = {
        "unique_resolutions": [f"{int(h)}x{int(w)}" for h, w in q_df[["height", "width"]].drop_duplicates().values],
        "height_mean": float(q_df["height"].mean()) if not q_df.empty else 0.0,
        "width_mean": float(q_df["width"].mean()) if not q_df.empty else 0.0,
    }

    intensity_stats = {
        "mean_pixel_intensity": float(q_df["mean_intensity"].mean()) if not q_df.empty else 0.0,
        "std_pixel_intensity": float(q_df["std_intensity"].mean()) if not q_df.empty else 0.0,
        "mean_sharpness_laplacian": float(q_df["sharpness"].mean()) if not q_df.empty else 0.0,
        "mean_entropy": float(q_df["entropy"].mean()) if not q_df.empty else 0.0,
    }

    # Grouped quality by alteration difficulty
    quality_by_difficulty = {}
    if not q_df.empty and "difficulty" in q_df.columns:
        for diff, group in q_df.groupby("difficulty"):
            quality_by_difficulty[str(diff)] = {
                "sharpness_mean": float(group["sharpness"].mean()),
                "contrast_mean": float(group["std_intensity"].mean()),
                "entropy_mean": float(group["entropy"].mean()),
            }

    eda_summary = {
        "total_images": total_images,
        "unique_subjects": unique_subjects,
        "unique_source_finger_groups": unique_source_groups,
        "num_original_images": num_original,
        "num_altered_images": num_altered,
        "subject_distribution": subject_stats,
        "finger_distribution": finger_counts,
        "finger_category_distribution": finger_category_counts,
        "hand_distribution": hand_counts,
        "gender_distribution": gender_counts,
        "alteration_category_distribution": alt_category_counts,
        "difficulty_distribution": difficulty_counts,
        "missing_original_analysis": {
            "expected_originals": expected_original_count,
            "actual_originals": num_original,
            "missing_originals": missing_original_count,
        },
        "corrupted_images_detected": len(corrupted_files),
        "corrupted_files_sample": corrupted_files[:10],
        "dimension_stats": dimension_stats,
        "intensity_and_quality_stats": intensity_stats,
        "quality_by_difficulty": quality_by_difficulty,
    }

    return eda_summary

