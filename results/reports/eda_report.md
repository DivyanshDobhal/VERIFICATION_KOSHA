# KOSHA LABS – SOCOFing Fingerprint Dataset Exploratory Analysis Report

## 1. Executive Summary
- **Total Images Analyzed:** 55,270
- **Unique Subjects:** 600
- **Unique Source Fingerprint Groups:** 6000
- **Original (Real) Fingerprints:** 6,000 (10.9%)
- **Altered Fingerprints:** 49,270 (89.1%)
- **Corrupted Images Detected:** 0

## 2. Subject & Acquisition Distributions
- **Images per Subject (Mean ± Std):** 92.12 ± 5.55
- **Subject Image Range:** Min: 61, Max: 100, Median: 94.0
- **Gender Breakdown (Images):** {"M": 44203, "F": 11067}

## 3. Alteration Types & Difficulty Levels
- **Alteration Categories:**
{
  "Obliteration": 17854,
  "Central Rotation": 16439,
  "Z-cut": 14977
}
- **Difficulty Distribution:**
{
  "Easy": 17931,
  "Medium": 17067,
  "Hard": 14272
}

## 4. Biometric Image Quality Analysis
- **Image Resolution:** 103x96, 298x241
- **Mean Pixel Intensity:** 145.49
- **Pixel Std Dev (Contrast):** 99.92
- **Sharpness (Laplacian Var):** 48981.41
- **Entropy:** 5.49

### Quality Breakdown by Difficulty
```json
{
  "Easy": {
    "sharpness_mean": 52258.42166020835,
    "contrast_mean": 101.79549066626436,
    "entropy_mean": 5.315588929206273
  },
  "Hard": {
    "sharpness_mean": 43082.32961719451,
    "contrast_mean": 97.17755937412393,
    "entropy_mean": 5.772076279917523
  },
  "Medium": {
    "sharpness_mean": 47663.30691203206,
    "contrast_mean": 99.39850755154555,
    "entropy_mean": 5.551123235437441
  },
  "Original": {
    "sharpness_mean": 58771.12046656914,
    "contrast_mean": 103.04615747082208,
    "entropy_mean": 5.1272273847757495
  }
}
```

## 5. Generated Visualizations
1. `eda_dataset_distributions.png`: Global compositions and categories.
2. `eda_finger_subject_distributions.png`: Subject histogram and finger-hand balance.
3. `eda_original_vs_altered_comparison.png`: Side-by-side alteration types.
4. `eda_difficulty_comparisons.png`: Easy, Medium, and Hard degradations.
5. `eda_random_samples_gallery.png`: Multi-subject fingerprint grid.
