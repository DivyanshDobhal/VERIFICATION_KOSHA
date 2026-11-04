"""
Execution script for Phase 1: SOCOFing Dataset Acquisition & EDA.
Runs scanning, parsing, quality profiling, metrics calculation, and visualization.
"""

import sys
from pathlib import Path
import json

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DATASET_ROOT, PLOTS_DIR, REPORTS_DIR
from ml.data.parser import scan_socofing_dataset
from ml.eda.analyzer import perform_eda
from ml.eda.visualizer import (
    plot_dataset_distributions,
    plot_finger_and_subject_distributions,
    plot_original_vs_altered_comparison,
    plot_difficulty_comparisons,
    plot_random_samples_gallery,
)


def generate_markdown_report(eda_summary: dict, output_file: Path):
    """Generates a professional markdown summary report."""
    md = f"""# KOSHA LABS – SOCOFing Fingerprint Dataset Exploratory Analysis Report

## 1. Executive Summary
- **Total Images Analyzed:** {eda_summary['total_images']:,}
- **Unique Subjects:** {eda_summary['unique_subjects']}
- **Unique Source Fingerprint Groups:** {eda_summary['unique_source_finger_groups']}
- **Original (Real) Fingerprints:** {eda_summary['num_original_images']:,} ({eda_summary['num_original_images']/eda_summary['total_images']*100:.1f}%)
- **Altered Fingerprints:** {eda_summary['num_altered_images']:,} ({eda_summary['num_altered_images']/eda_summary['total_images']*100:.1f}%)
- **Corrupted Images Detected:** {eda_summary['corrupted_images_detected']}

## 2. Subject & Acquisition Distributions
- **Images per Subject (Mean ± Std):** {eda_summary['subject_distribution']['mean']:.2f} ± {eda_summary['subject_distribution']['std']:.2f}
- **Subject Image Range:** Min: {eda_summary['subject_distribution']['min']}, Max: {eda_summary['subject_distribution']['max']}, Median: {eda_summary['subject_distribution']['median']}
- **Gender Breakdown (Images):** {json.dumps(eda_summary['gender_distribution'])}

## 3. Alteration Types & Difficulty Levels
- **Alteration Categories:**
{json.dumps(eda_summary['alteration_category_distribution'], indent=2)}
- **Difficulty Distribution:**
{json.dumps(eda_summary['difficulty_distribution'], indent=2)}

## 4. Biometric Image Quality Analysis
- **Image Resolution:** {', '.join(eda_summary['dimension_stats']['unique_resolutions'])}
- **Mean Pixel Intensity:** {eda_summary['intensity_and_quality_stats']['mean_pixel_intensity']:.2f}
- **Pixel Std Dev (Contrast):** {eda_summary['intensity_and_quality_stats']['std_pixel_intensity']:.2f}
- **Sharpness (Laplacian Var):** {eda_summary['intensity_and_quality_stats']['mean_sharpness_laplacian']:.2f}
- **Entropy:** {eda_summary['intensity_and_quality_stats']['mean_entropy']:.2f}

### Quality Breakdown by Difficulty
```json
{json.dumps(eda_summary['quality_by_difficulty'], indent=2)}
```

## 5. Generated Visualizations
1. `eda_dataset_distributions.png`: Global compositions and categories.
2. `eda_finger_subject_distributions.png`: Subject histogram and finger-hand balance.
3. `eda_original_vs_altered_comparison.png`: Side-by-side alteration types.
4. `eda_difficulty_comparisons.png`: Easy, Medium, and Hard degradations.
5. `eda_random_samples_gallery.png`: Multi-subject fingerprint grid.
"""
    output_file.write_text(md)
    print(f"Generated Markdown Report: {output_file}")


def main():
    print("=" * 60)
    print("PHASE 1: SOCOFing Dataset Acquisition and Exploratory Analysis")
    print(f"Dataset root: {DATASET_ROOT}")
    print("=" * 60)

    if not DATASET_ROOT.exists():
        print(f"Error: Dataset path {DATASET_ROOT} does not exist.")
        sys.exit(1)

    print("Step 1: Scanning and parsing all image filenames...")
    df = scan_socofing_dataset(DATASET_ROOT)
    print(f"Successfully discovered and parsed {len(df):,} images.")

    print("\nStep 2: Performing Statistical and Biometric Quality EDA...")
    eda_summary = perform_eda(df, sample_quality_size=1200)

    # Save summary json
    json_path = REPORTS_DIR / "eda_summary.json"
    with open(json_path, "w") as f:
        json.dump(eda_summary, f, indent=2)
    print(f"Saved EDA Summary JSON: {json_path}")

    # Generate Markdown report
    md_path = REPORTS_DIR / "eda_report.md"
    generate_markdown_report(eda_summary, md_path)

    print("\nStep 3: Generating High-Resolution Publication Figures...")
    plot_dataset_distributions(df, PLOTS_DIR)
    plot_finger_and_subject_distributions(df, PLOTS_DIR)
    plot_original_vs_altered_comparison(df, PLOTS_DIR)
    plot_difficulty_comparisons(df, PLOTS_DIR)
    plot_random_samples_gallery(df, PLOTS_DIR)

    # Also save the parsed dataset index as a parquet or csv for fast loading in subsequent phases
    index_csv = REPORTS_DIR / "socofing_parsed_metadata.csv"
    df.to_csv(index_csv, index=False)
    print(f"Saved Parsed Dataset Metadata CSV: {index_csv}")
    print("\nPhase 1 Completed Successfully.")


if __name__ == "__main__":
    main()

