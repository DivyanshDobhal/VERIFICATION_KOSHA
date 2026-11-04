# Machine Learning Subsystem (`ml/`)
**Kosha Labs Biometric Fingerprint Recognition & Identification**

This folder encapsulates all machine learning components, models, training procedures, evaluation routines, datasets parsing, preprocessing pipelines, and trained checkpoints for the fingerprint biometric recognition system.

> **Biometric Modality:** Fingerprint Verification & Identification (*strictly fingerprint recognition, not facial recognition*).

---

## Directory Organization

```
ml/
├── __init__.py                # ML package entry point
├── engine.py                  # High-level BiometricInferenceEngine (feature extraction & 1:1 matching)
│
├── data/                      # Dataset ingestion and zero-leakage splitting
│   ├── parser.py              # SOCOFing filename metadata extraction (subjects, fingers, alterations)
│   ├── split.py               # Protocol A (disjoint source groups) & Protocol B (disjoint subjects)
│   └── pair_generator.py      # Balanced positive/negative Siamese pair generator with group isolation
│
├── preprocessing/             # Biometric signal processing & augmentation
│   ├── pipeline.py            # CLAHE, bilateral ridge filtering, 128x128 resize, Laplacian validation
│   └── augmentation.py        # Biometric-safe augmentations (rotation <= 12 deg, minor noise/contrast)
│
├── models/                    # Neural architectures & loss functions
│   ├── losses.py              # Contrastive loss with margin & Euclidean distance layer
│   ├── siamese_cnn.py         # Primary 4-stage Siamese CNN with 128-D L2-normalized embeddings
│   ├── resnet_baseline.py     # ResNet50 Siamese transfer-learning backbone
│   ├── mobilenet_baseline.py  # MobileNetV3 Siamese lightweight mobile backbone
│   └── hog_svm_baseline.py    # Classical HOG feature descriptor baseline
│
├── training/                  # Model training & optimization routines
│   ├── trainer.py             # Custom training loop with contrastive loss and gradient descent
│   ├── cross_validator.py     # 5-fold Stratified Group Cross-Validation on source groups
│   └── tuner.py               # Stratified hyperparameter optimization across margins and optimizers
│
├── evaluation/                # Biometric evaluation suite
│   ├── metrics.py             # EER, FAR, FRR, ROC-AUC, PR-AUC, Rank-1, Rank-5, MRR
│   └── evaluator.py           # Verification and open-set identification evaluation with 95% CIs
│
├── visualization/             # Diagnostic and analytical plotting
│   ├── plot_curves.py         # ROC, PR, EER, confusion matrices, and training curves
│   └── plot_embeddings.py     # PCA and t-SNE 2D manifold projections of fingerprint embeddings
│
├── scripts/                   # Standalone execution runners
│   ├── eda.py                 # Exploratory data analysis runner
│   ├── preprocess.py          # Preprocessing demonstration runner
│   ├── split.py               # Protocol A and B data splitting runner
│   ├── train.py               # 5-fold cross-validation and final model training runner
│   ├── evaluate.py            # Comprehensive evaluation on holdout test set
│   ├── compare.py             # Multi-architecture benchmarking runner
│   └── tune.py                # Hyperparameter tuning grid runner
│
├── checkpoints/               # Symlink to model weights & calibrated thresholds
│   ├── siamese_cnn_final.weights.h5
│   ├── calibrated_thresholds.json
│   └── fold_1_best_siamese_model.weights.h5 ... fold_5
│
└── results/                   # Symlink to generated evaluation plots and analytical reports
    ├── plots/                 # High-resolution PNG figures
    └── reports/               # JSON metrics, split registries, and technical reports
```

---

## Quick Usage

### 1. Extract 128-D Embedding & Verify Pairs in Python
```python
from ml.engine import BiometricInferenceEngine

engine = BiometricInferenceEngine()

# 128-D L2-normalized embedding
embedding = engine.extract_embedding("path/to/fingerprint.BMP")
print("Embedding shape:", embedding.shape)  # (128,)

# 1:1 Verification
result = engine.verify("fingerprint_a.BMP", "fingerprint_b.BMP", security_level="standard")
print(result)
# {'is_match': True, 'euclidean_distance': 0.0182, 'threshold_used': 0.0200, 'confidence_score': 0.7725}
```

### 2. Run ML Training & Evaluation Scripts
```bash
# 5-Fold Stratified Group Cross-Validation & Model Training
python ml/scripts/train.py

# Multi-Architecture Benchmark (Siamese CNN vs ResNet50 vs MobileNet vs HOG)
python ml/scripts/compare.py

# Full Holdout Evaluation & Manifold Visualizations (PCA / t-SNE)
python ml/scripts/evaluate.py
```

