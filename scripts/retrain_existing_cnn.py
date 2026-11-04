"""
KOSHA LABS – Biometric Siamese CNN Model Retraining and Calibration Script.
Strict Requirement: Retains the EXACT existing 4-block Siamese CNN architecture
(src/models/siamese_cnn.py) with zero architecture modifications.
Repairs dataset pairing logic, trains with clean genuine and hard-negative pairs,
recalibrates operational decision thresholds, and validates on unseen test identities.
"""

import os
import sys
import time
import json
from pathlib import Path

# 1. OpenMP & TensorFlow Thread Bounds for macOS stability
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["TF_NUM_INTRAOP_THREADS"] = "2"
os.environ["TF_NUM_INTEROP_THREADS"] = "2"

# 2. CRITICAL: Import TensorFlow BEFORE pandas/pyarrow to avoid Abseil symbol collision deadlock
import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 3. Import pandas and project settings
import numpy as np
import pandas as pd
from config.settings import CHECKPOINTS_DIR, REPORTS_DIR, PLOTS_DIR
from src.models.siamese_cnn import build_siamese_network
from src.models.losses import contrastive_loss
from src.data.pair_generator import FingerprintPairGenerator, load_pair_arrays
from src.preprocessing.pipeline import FingerprintPreprocessor
from src.preprocessing.augmentation import BiometricAugmentor
from src.evaluation.metrics import (
    compute_classification_metrics,
    compute_biometric_verification_metrics,
)
from src.service.threshold import ThresholdOptimizer


def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def main():
    log("=" * 70)
    log("KOSHA LABS – SIAMESE CNN RETRAINING & CALIBRATION PIPELINE")
    log("Preserving exact 4-Block Siamese CNN Architecture (488,448 params)")
    log("=" * 70)

    # 1. Load Partitioned Splits (Protocol B: Subject-Disjoint)
    split_dir = REPORTS_DIR / "splits"
    train_csv = split_dir / "protocol_b_train.csv"
    val_csv = split_dir / "protocol_b_val.csv"
    test_csv = split_dir / "protocol_b_test.csv"

    if not train_csv.exists() or not val_csv.exists() or not test_csv.exists():
        log("Error: Protocol B split CSVs not found in results/reports/splits/")
        sys.exit(1)

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)
    test_df = pd.read_csv(test_csv)
    log(f"Dataset Pools Loaded:")
    log(f"  Train: {len(train_df):,} images | {train_df['subject_id'].nunique()} subjects | {train_df['source_finger_group'].nunique()} finger groups")
    log(f"  Val:   {len(val_df):,} images | {val_df['subject_id'].nunique()} subjects | {val_df['source_finger_group'].nunique()} finger groups")
    log(f"  Test:  {len(test_df):,} images | {test_df['subject_id'].nunique()} subjects | {test_df['source_finger_group'].nunique()} finger groups")

    # 2. Setup Pair Generators with Repaired Logic
    preprocessor = FingerprintPreprocessor()
    augmentor = BiometricAugmentor(seed=42)

    log("Generating clean, balanced training, validation, and test pairs...")
    train_gen = FingerprintPairGenerator(train_df, seed=42)
    val_gen = FingerprintPairGenerator(val_df, seed=100)
    test_gen = FingerprintPairGenerator(test_df, seed=999)

    # Balanced pair counts
    n_train_pairs = 1600
    n_val_pairs = 300
    n_test_pairs = 500

    train_p1, train_p2, train_y = train_gen.generate_pairs(num_pairs=n_train_pairs, hard_negative_ratio=0.5)
    val_p1, val_p2, val_y = val_gen.generate_pairs(num_pairs=n_val_pairs, hard_negative_ratio=0.5)
    test_p1, test_p2, test_y = test_gen.generate_pairs(num_pairs=n_test_pairs, hard_negative_ratio=0.5)

    log(f"Pairs Generated:")
    log(f"  Train: {len(train_y)} pairs (Genuine: {int(np.sum(train_y == 1))}, Imposter: {int(np.sum(train_y == 0))})")
    log(f"  Val:   {len(val_y)} pairs (Genuine: {int(np.sum(val_y == 1))}, Imposter: {int(np.sum(val_y == 0))})")
    log(f"  Test:  {len(test_y)} pairs (Genuine: {int(np.sum(test_y == 1))}, Imposter: {int(np.sum(test_y == 0))})")

    # 3. Preload & Preprocess Image Arrays
    log("Preloading and preprocessing image arrays with CLAHE enhancement...")
    t0_prep = time.time()
    (train_x1, train_x2), train_y_arr = load_pair_arrays(
        train_p1, train_p2, train_y, preprocessor=preprocessor, augmentor=augmentor
    )
    (val_x1, val_x2), val_y_arr = load_pair_arrays(
        val_p1, val_p2, val_y, preprocessor=preprocessor, augmentor=None
    )
    (test_x1, test_x2), test_y_arr = load_pair_arrays(
        test_p1, test_p2, test_y, preprocessor=preprocessor, augmentor=None
    )
    log(f"Preprocessing completed in {time.time() - t0_prep:.2f}s.")

    # 4. Build Exact Existing Siamese CNN Architecture
    log("Instantiating EXACT Siamese CNN architecture...")
    siamese_model, feature_extractor = build_siamese_network(
        input_shape=(128, 128, 1),
        embedding_dim=128,
        dropout_rate=0.3,
    )

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    siamese_model.compile(
        optimizer=optimizer,
        loss=contrastive_loss(margin=1.0),
    )

    log(f"Model Summary: Total params: {siamese_model.count_params():,}")
    log(f"Feature Extractor params: {feature_extractor.count_params():,}")

    # 5. Model Callbacks
    best_weights_path = CHECKPOINTS_DIR / "siamese_cnn_final.weights.h5"
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(best_weights_path),
            monitor="val_loss",
            save_best_only=True,
            save_weights_only=True,
            verbose=1,
        ),
    ]

    # 6. Retraining Execution (verbose=2 for clean line logging)
    epochs = 8
    batch_size = 32
    log(f"Starting Siamese CNN retraining ({epochs} epochs, batch_size={batch_size})...")
    t0_train = time.time()
    history = siamese_model.fit(
        [train_x1, train_x2],
        train_y_arr,
        validation_data=([val_x1, val_x2], val_y_arr),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=2,
    )
    train_duration = time.time() - t0_train
    log(f"Retraining completed in {train_duration:.2f}s.")

    # Also save as best_siamese_model.weights.h5
    siamese_model.save_weights(str(CHECKPOINTS_DIR / "best_siamese_model.weights.h5"))
    log(f"Saved retrained weights to {best_weights_path} and best_siamese_model.weights.h5")

    # 7. Threshold Calibration on Validation Partition
    log("Calibrating decision thresholds on validation partition...")
    val_distances = siamese_model.predict([val_x1, val_x2], batch_size=batch_size, verbose=0).flatten()

    val_pos_dist = val_distances[val_y_arr == 1.0]
    val_neg_dist = val_distances[val_y_arr == 0.0]
    log(f"Val Genuine distances: mean={val_pos_dist.mean():.4f}, median={np.median(val_pos_dist):.4f}, std={val_pos_dist.std():.4f}")
    log(f"Val Imposter distances: mean={val_neg_dist.mean():.4f}, median={np.median(val_neg_dist):.4f}, std={val_neg_dist.std():.4f}")

    thresh_optimizer = ThresholdOptimizer(CHECKPOINTS_DIR / "calibrated_thresholds.json")
    calibrated = thresh_optimizer.calibrate(val_y_arr, val_distances, save=True)
    log("Calibrated Thresholds:")
    for k, v in calibrated.items():
        log(f"  {k}: {v:.4f}")

    # 8. Rigorous Test Partition Evaluation
    log("Evaluating on independent test partition (90 unseen subjects, 900 unseen fingers)...")
    t0_test = time.time()
    test_distances = siamese_model.predict([test_x1, test_x2], batch_size=batch_size, verbose=0).flatten()
    infer_time = time.time() - t0_test

    latency_ms = (infer_time / len(test_y_arr)) * 1000.0
    throughput = len(test_y_arr) / infer_time if infer_time > 0 else 0.0

    test_pos_dist = test_distances[test_y_arr == 1.0]
    test_neg_dist = test_distances[test_y_arr == 0.0]
    log(f"Test Genuine distances (n={len(test_pos_dist)}): min={test_pos_dist.min():.4f}, mean={test_pos_dist.mean():.4f}, median={np.median(test_pos_dist):.4f}, max={test_pos_dist.max():.4f}")
    log(f"Test Imposter distances (n={len(test_neg_dist)}): min={test_neg_dist.min():.4f}, mean={test_neg_dist.mean():.4f}, median={np.median(test_neg_dist):.4f}, max={test_neg_dist.max():.4f}")

    # Compute Biometric Verification & Classification Metrics at Standard Threshold
    bio_metrics = compute_biometric_verification_metrics(test_y_arr, test_distances)
    eval_threshold = calibrated["standard_far_1_threshold"]
    class_metrics = compute_classification_metrics(test_y_arr, test_distances, threshold=eval_threshold)

    log("=" * 70)
    log("TEST SET EVALUATION RESULTS:")
    log(f"  Accuracy:          {class_metrics['accuracy']*100:.2f}%")
    log(f"  Precision:         {class_metrics['precision']*100:.2f}%")
    log(f"  Recall (GAR):      {class_metrics['recall']*100:.2f}%")
    log(f"  Specificity:       {class_metrics['specificity']*100:.2f}%")
    log(f"  F1 Score:          {class_metrics['f1_score']:.4f}")
    log(f"  Balanced Accuracy: {class_metrics['balanced_accuracy']*100:.2f}%")
    log(f"  MCC:               {class_metrics['matthews_corrcoef']:.4f}")
    log(f"  EER:               {bio_metrics['eer']*100:.2f}% (at d={bio_metrics['eer_threshold_distance']:.4f})")
    log(f"  ROC-AUC:           {bio_metrics['roc_auc']:.4f}")
    log(f"  PR-AUC:            {bio_metrics['pr_auc']:.4f}")
    log(f"  TAR @ FAR=1.0%:    {bio_metrics['tar_at_far_1_percent']*100:.2f}%")
    log(f"  Inference Latency: {latency_ms:.2f} ms/pair")
    log(f"  Throughput:        {throughput:.1f} pairs/sec")
    log(f"  Confusion Matrix:  {class_metrics['confusion_matrix']}")
    log("=" * 70)

    # 9. Save Full Evaluation Report
    eval_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_architecture": "Siamese CNN (4-Block Conv + L2-Normalized 128-D Embedding)",
        "protocol": "Protocol B: Subject-Disjoint Generalization",
        "num_pairs_evaluated": len(test_y_arr),
        "performance": {
            "training_time_seconds": train_duration,
            "inference_time_seconds": infer_time,
            "latency_ms_per_pair": latency_ms,
            "throughput_pairs_per_sec": throughput,
            "total_parameters": int(siamese_model.count_params()),
            "trainable_parameters": int(np.sum([tf.keras.backend.count_params(w) for w in siamese_model.trainable_weights])),
        },
        "calibrated_thresholds": calibrated,
        "biometric_verification": bio_metrics,
        "classification": class_metrics,
        "history": {k: [float(val) for val in v] for k, v in history.history.items()},
    }

    report_path = REPORTS_DIR / "retrained_cnn_evaluation.json"
    with open(report_path, "w") as f:
        json.dump(eval_report, f, indent=2)
    log(f"Saved evaluation report to: {report_path}")

    # Also update siamese_cnn_test_metrics.json
    metrics_path = REPORTS_DIR / "siamese_cnn_test_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(eval_report, f, indent=2)
    log(f"Updated test metrics in: {metrics_path}")

    log("Retraining and Calibration Pipeline Completed Successfully!")


if __name__ == "__main__":
    main()
