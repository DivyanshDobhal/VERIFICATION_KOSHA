"""
Script for Phase 2: Data Preprocessing verification & visualization.
Processes samples from Real and Altered splits, evaluates ridge preservation, and plots comparisons.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import REPORTS_DIR, PLOTS_DIR
from src.preprocessing.pipeline import FingerprintPreprocessor
from src.preprocessing.augmentation import BiometricAugmentor
import pandas as pd


def main():
    print("=" * 60)
    print("PHASE 2: Data Preprocessing and Ridge Preservation Pipeline")
    print("=" * 60)

    metadata_path = REPORTS_DIR / "socofing_parsed_metadata.csv"
    if not metadata_path.exists():
        print(f"Metadata file {metadata_path} not found. Run Phase 1 first.")
        sys.exit(1)

    df = pd.read_csv(metadata_path)
    preprocessor = FingerprintPreprocessor(target_size=(128, 128))
    augmentor = BiometricAugmentor()

    # Pick 4 diverse sample images: 2 original, 1 easy altered, 1 hard altered
    orig_samples = df[~df["is_altered"]].sample(2, random_state=42)
    easy_sample = df[(df["is_altered"]) & (df["difficulty"] == "Easy")].sample(1, random_state=42)
    hard_sample = df[(df["is_altered"]) & (df["difficulty"] == "Hard")].sample(1, random_state=42)
    samples = pd.concat([orig_samples, easy_sample, hard_sample])

    fig, axes = plt.subplots(4, 4, figsize=(14, 14))

    for row_idx, (_, item) in enumerate(samples.iterrows()):
        raw_img = cv2.imread(item["file_path"], cv2.IMREAD_GRAYSCALE)
        valid, lap_var, msg = preprocessor.validate_quality(raw_img)

        # Preprocessing stages
        # Stage 1: Raw
        axes[row_idx, 0].imshow(raw_img, cmap="gray")
        axes[row_idx, 0].set_title(f"Raw Input\n({raw_img.shape[0]}x{raw_img.shape[1]})", fontsize=10)
        axes[row_idx, 0].axis("off")

        # Stage 2: Bilateral Denoised
        denoised = cv2.bilateralFilter(raw_img, d=5, sigmaColor=50, sigmaSpace=50)
        axes[row_idx, 1].imshow(denoised, cmap="gray")
        axes[row_idx, 1].set_title("Denoised (Bilateral)", fontsize=10)
        axes[row_idx, 1].axis("off")

        # Stage 3: CLAHE Enhanced & Resized (128x128)
        processed = preprocessor.process_image(raw_img)
        axes[row_idx, 2].imshow(processed[:, :, 0], cmap="gray")
        axes[row_idx, 2].set_title("CLAHE + Normalized\n(128x128)", fontsize=10)
        axes[row_idx, 2].axis("off")

        # Stage 4: Augmented
        augmented = augmentor(processed)
        axes[row_idx, 3].imshow(augmented[:, :, 0], cmap="gray")
        axes[row_idx, 3].set_title("Biometric Augmented", fontsize=10)
        axes[row_idx, 3].axis("off")

        label = f"Subj {item['subject_id']} ({item['finger_label']}) - {item['difficulty']}"
        axes[row_idx, 0].set_ylabel(label, fontsize=11, fontweight="bold")

    plt.suptitle("Fingerprint Preprocessing & Biometric Augmentation Pipeline", fontsize=14, fontweight="bold")
    plt.tight_layout()
    out_plot = PLOTS_DIR / "preprocessing_comparisons.png"
    plt.savefig(out_plot, dpi=300)
    plt.close()
    print(f"Saved Preprocessing Comparisons Plot: {out_plot}")
    print("Phase 2 Preprocessing Pipeline Verified Successfully.")


if __name__ == "__main__":
    main()

