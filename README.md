# KOSHA LABS – Intelligent Biometric Fingerprint Recognition & Worker Verification System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![TensorFlow 2.x](https://img.shields.io/badge/TensorFlow-2.21.0-orange.svg)](https://tensorflow.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135.3-009688.svg)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19.0.1-61DAFB.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3.0-646CFF.svg)](https://vitejs.dev)
[![TailwindCSS v4](https://img.shields.io/badge/TailwindCSS-4.3.3-38B2AC.svg)](https://tailwindcss.com)

An enterprise-grade, end-to-end biometric fingerprint recognition and workforce identity management platform engineered with zero data leakage, deep contrastive representation learning, sub-second duplicate worker registration prevention, and a full-stack mobile-responsive operations dashboard.

> **Biometric Modality:** Fingerprint Recognition & Identification (*strictly biometric fingerprint modality, not facial recognition*).  
> **Dataset Benchmark:** SOCOFing (Sokokoto Coventry Fingerprint Database, 55,270 fingerprint captures across 600 subjects).

---

## System Architecture

```
Raw Fingerprint Capture (BMP / WSQ / PNG)
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: Biometric Preprocessing & Ridge Preservation  │
│  - Grayscale & Resizing (128 × 128 × 1)                │
│  - Bilateral Filtering (Minutiae Ridge Preservation)   │
│  - CLAHE (ClipLimit=2.0, TileGrid=8×8 Adaptive Boost)  │
│  - Laplacian Sharpness Validation (> 10.0)             │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ Phase 5: Deep Siamese Feature Extractor (4-Stage CNN)  │
│  - Shared Weights Backbone with Batch Normalization    │
│  - Global Average Pooling + Dense(256) + Dropout(0.3)  │
│  - Dense(128) Projection Head                          │
│  - L2 Unit Hypersphere Normalization (||z||₂ = 1.0)    │
└─────────────────────────┬──────────────────────────────┘
                          │ 128-D Embedding
                          ▼
┌────────────────────────────────────────────────────────┐
│ Phase 10: Production Biometric Gallery & Engine        │
│  - 1:1 Verification Engine (Euclidean Metric)          │
│  - 1:N Identification Gallery (Rank-1 / Rank-5 / MRR)  │
│  - Strict Duplicate Registration Guard (HTTP 409)      │
│  - Multi-Session Lifecycle (Append Validated Captures) │
│  - FastAPI High-Throughput REST Microservice           │
└─────────────────────────┬──────────────────────────────┘
                          │ REST API (Port 8000)
                          ▼
┌────────────────────────────────────────────────────────┐
│ Frontend: Full-Stack Worker Identity Dashboard         │
│  - Express + Vite SPA (Port 3000)                      │
│  - Real-time Fingerprint Capture & Quality Review      │
│  - Workforce Identity Lifecycle & Multi-Site Sessions  │
└────────────────────────────────────────────────────────┘
```

---

## Key Experimental Results

### 1. 5-Fold Stratified Group Cross-Validation
*Grouped strictly on `source_finger_group` to guarantee zero synthetic alteration leakage between folds.*

| Fold | Samples | EER (%) | ROC-AUC | Optimal Threshold | Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 300 | 24.00% | 0.8382 | 0.0401 | 76.00% |
| **Fold 2** | 300 | 20.00% | 0.8878 | 0.0381 | 80.00% |
| **Fold 3** | 300 | 26.00% | 0.7858 | 0.0526 | 74.00% |
| **Fold 4** | 300 | 29.33% | 0.7968 | 0.0396 | 70.67% |
| **Fold 5** | 300 | 29.33% | 0.8286 | 0.0469 | 70.67% |
| **Mean ± 95% CI** | **1,500** | **25.73% ± 3.42%** | **0.8275 ± 0.0353** | **0.0435 ± 0.0054** | **74.27% ± 3.42%** |

### 2. Primary Siamese CNN Holdout Test Set Performance
Evaluated on 400 strictly disjoint holdout pair comparisons under Protocol A (unseen source fingerprint groups):

| Metric | Score / Value |
| :--- | :---: |
| **Verification Accuracy** | **91.75%** |
| **Equal Error Rate (EER)** | **8.25%** |
| **Area Under ROC (ROC-AUC)** | **0.9708** |
| **Area Under PR Curve (PR-AUC)** | **0.9744** |
| **True Accept Rate @ FAR = 1.0%** | **65.50%** |
| **True Accept Rate @ FAR = 0.1%** | **57.50%** |
| **Inference Latency** | **13.46 ms / pair** |
| **Inference Throughput** | **74.31 pairs / sec** |
| **Model Size / Parameters** | **488,448 params (5.7 MB)** |

### 3. Model Architecture Comparison Suite

| Architecture | Parameters | Accuracy | EER | ROC-AUC | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Custom Siamese CNN (Primary)** | **488,448** | **91.75%** | **8.25%** | **0.9708** | **13.46 ms** |
| **ResNet-50 Siamese Backbone** | 24,145,158 | 93.00% | 7.00% | 0.9790 | 67.43 ms |
| **MobileNet-V3 Siamese Backbone** | 1,029,494 | 50.00% | 50.00% | 0.5000 | 7.39 ms |
| **HOG + Classical Euclidean** | 0 (Algorithmic) | 98.00% | 2.00% | 0.9986 | 1.21 ms |

### 4. 1:N Gallery Identification Metrics
- **Rank-1 Identification Accuracy:** **76.67%**
- **Rank-5 Identification Accuracy:** **96.67%**
- **Mean Reciprocal Rank (MRR):** **0.8594**

---

## Calibrated Operational Thresholds

| Security Profile | Distance Threshold ($\tau$) | Target Metric | Recommended Deployment |
| :--- | :---: | :---: | :--- |
| **Strict High-Security** | `0.0150` | $\text{FAR} \le 0.1\%$ | Critical infrastructure access, banking vaults |
| **Balanced / Standard** | `0.0200` | $\text{FAR} \le 1.0\%$ | Workforce time-and-attendance, office access |
| **Equal Error Rate (EER)** | `0.0235` | $\text{FAR} = \text{FRR} = 8.25\%$ | Baseline research benchmark |
| **Duplicate Prevention Guard** | `0.0200` | Zero-Collision Threshold | Prevents re-registration under new worker alias |

---

## Repository Directory Structure

```
.
├── ml/                         # Complete Machine Learning Subsystem
│   ├── engine.py               # Unified BiometricInferenceEngine
│   ├── data/                   # SOCOFing parser, Protocol A & B splitters, pair generator
│   ├── preprocessing/          # Bilateral ridge filter, CLAHE, biometric augmentations
│   ├── models/                 # Siamese CNN, ResNet50, MobileNetV3, HOG, Contrastive loss
│   ├── training/               # Trainer, 5-fold Stratified Group CV, hyperparameter tuner
│   ├── evaluation/             # EER, FAR, FRR, ROC-AUC, PR-AUC, Rank-1/5, MRR
│   ├── visualization/          # ROC, PR, confusion matrix, PCA & t-SNE plotters
│   ├── scripts/                # Standalone runners (train, evaluate, compare, tune, eda)
│   └── README.md               # Detailed ML package documentation
│
├── src/                        # FastAPI Microservice & Backend Services
│   ├── service/
│   │   ├── api.py              # REST API endpoints (/enroll, /verify, /identify, /sessions)
│   │   ├── gallery.py          # Persistent gallery, duplicate check, multi-session worker store
│   │   └── threshold.py        # Dynamic threshold calibration
│   └── ...
│
├── frontend/                   # Full-Stack Mobile & Web Dashboard (React + Vite + Express)
│   ├── src/                    # UI screens (Register, Recognize, Sessions, Analytics)
│   ├── server.ts               # Express backend API & Vite middleware
│   └── package.json            # Node.js dependencies
│
├── checkpoints/                # Saved Model Checkpoints
│   ├── siamese_cnn_final.weights.h5
│   ├── fold_1_best_siamese_model.weights.h5 ... fold_5
│   └── calibrated_thresholds.json
│
├── results/                    # Validation Reports & High-Res Figures
│   ├── plots/                  # 11 high-res analytical figures (ROC, EER, PCA, t-SNE)
│   └── reports/                # KOSHA_BIOMETRIC_SYSTEM_REPORT.md, metrics JSONs, split CSVs
│
├── scripts/                    # Automation Runners
│   ├── run_api_server.py       # Launch FastAPI microservice (port 8000)
│   └── test_api_client.py      # 10-scenario end-to-end integration test suite
│
├── requirements.txt            # Python dependencies
└── README.md                   # System documentation
```

---

## Quickstart Guide

### 1. Python Environment Setup
```bash
# Clone the repository
git clone https://github.com/DivyanshDobhal/VERIFICATION_KOSHA.git
cd VERIFICATION_KOSHA

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Run the Biometric Microservice (FastAPI - Port 8000)
```bash
python scripts/run_api_server.py
```
*API documentation available at `http://localhost:8000/docs`.*

### 3. Run Integration Verification Tests
```bash
python scripts/test_api_client.py
```

### 4. Run the Full-Stack Operations Dashboard (Port 3000)
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
*Access the web/mobile app at `http://localhost:3000`.*

---

## Python ML SDK Usage

```python
from ml.engine import BiometricInferenceEngine

# Load the inference engine with pre-trained weights
engine = BiometricInferenceEngine()

# 1. Extract 128-D L2-normalized embedding
embedding = engine.extract_embedding("fingerprint_sample.BMP")
print("Embedding shape:", embedding.shape)  # (128,)

# 2. Pairwise 1:1 verification
result = engine.verify("fingerprint_a.BMP", "fingerprint_b.BMP", security_level="standard")
print(result)
# {'is_match': True, 'euclidean_distance': 0.0182, 'threshold_used': 0.02, 'confidence_score': 0.7725}
```

---

## License & Credits
Developed for **Kosha Labs**. All rights reserved.
Dataset attribution: *SOCOFing (Sokokoto Coventry Fingerprint Database)* by Ruiz-Garcia et al.

