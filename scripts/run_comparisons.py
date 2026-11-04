"""
Execution script for Phase 6: Model Comparisons.
Compares:
1. Siamese CNN (Custom Architecture)
2. ResNet50 (Transfer Backbone)
3. MobileNetV3 (Lightweight Mobile Edge)
4. HOG + SVM (Classical Baseline)
Evaluates on identical test sets under consistent protocol.
"""

import tensorflow as tf
import sys
from pathlib import Path
import json
import time
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import REPORTS_DIR, CHECKPOINTS_DIR, PLOTS_DIR
from src.models.siamese_cnn import build_siamese_network
from src.models.resnet_baseline import build_resnet_siamese_network
from src.models.mobilenet_baseline import build_mobilenet_siamese_network
from src.models.hog_svm_baseline import HOGFeatureExtractor, HOGSVMVerifier
from src.models.losses import contrastive_loss
from src.data.pair_generator import FingerprintPairGenerator, load_pair_arrays
from src.evaluation.evaluator import evaluate_verification
from src.visualization.plot_curves import plot_model_comparisons
from src.preprocessing.pipeline import FingerprintPreprocessor


def main():
    print("=" * 70)
    print("PHASE 6: Benchmark Model Comparisons")
    print("=" * 70)

    split_dir = REPORTS_DIR / "splits"
    train_csv = split_dir / "protocol_a_train.csv"
    val_csv = split_dir / "protocol_a_val.csv"
    test_csv = split_dir / "protocol_a_test.csv"

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)
    test_df = pd.read_csv(test_csv)

    preprocessor = FingerprintPreprocessor()

    # Generate identical training, validation, and test pairs for all deep learning models
    print("Generating consistent evaluation pairs across models...")
    train_factory = FingerprintPairGenerator(train_df, seed=42)
    val_factory = FingerprintPairGenerator(val_df, seed=100)
    test_factory = FingerprintPairGenerator(test_df, seed=999)

    t_p1, t_p2, t_y = train_factory.generate_pairs(num_pairs=400)
    v_p1, v_p2, v_y = val_factory.generate_pairs(num_pairs=150)
    te_p1, te_p2, te_y = test_factory.generate_pairs(num_pairs=400)

    (tx1, tx2), ty = load_pair_arrays(t_p1, t_p2, t_y, preprocessor=preprocessor)
    (vx1, vx2), vy = load_pair_arrays(v_p1, v_p2, v_y, preprocessor=preprocessor)

    comparison_results = []

    # ------------------ MODEL 1: Custom Siamese CNN ------------------
    print("\n--- Model 1: Primary Siamese CNN ---")
    siamese_cnn, _ = build_siamese_network()
    primary_ckpt = CHECKPOINTS_DIR / "siamese_cnn_final.weights.h5"
    if primary_ckpt.exists():
        siamese_cnn.load_weights(str(primary_ckpt))
        print("Loaded pre-trained weights for Siamese CNN.")
    else:
        siamese_cnn.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss=contrastive_loss(1.0))
        siamese_cnn.fit([tx1, tx2], ty, validation_data=([vx1, vx2], vy), batch_size=32, epochs=4, verbose=1)

    eval_cnn = evaluate_verification(siamese_cnn, te_p1, te_p2, te_y, preprocessor=preprocessor)
    comparison_results.append({
        "model_name": "Siamese CNN (Custom)",
        "accuracy": eval_cnn["classification"]["accuracy"],
        "eer": eval_cnn["biometric_verification"]["eer"],
        "roc_auc": eval_cnn["biometric_verification"]["roc_auc"],
        "tar_at_1_percent_far": eval_cnn["biometric_verification"]["tar_at_far_1_percent"],
        "latency_ms": eval_cnn["performance"]["latency_ms_per_pair"],
        "throughput_pairs_sec": eval_cnn["performance"]["throughput_pairs_per_sec"],
        "parameters": eval_cnn["performance"]["total_parameters"],
    })
    tf.keras.backend.clear_session()

    # ------------------ MODEL 2: ResNet50 Siamese ------------------
    print("\n--- Model 2: ResNet50 Siamese ---")
    resnet_model, _ = build_resnet_siamese_network()
    resnet_model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss=contrastive_loss(1.0))
    resnet_model.fit([tx1, tx2], ty, validation_data=([vx1, vx2], vy), batch_size=32, epochs=1, verbose=2)

    eval_resnet = evaluate_verification(resnet_model, te_p1, te_p2, te_y, preprocessor=preprocessor)
    comparison_results.append({
        "model_name": "ResNet50 Siamese",
        "accuracy": eval_resnet["classification"]["accuracy"],
        "eer": eval_resnet["biometric_verification"]["eer"],
        "roc_auc": eval_resnet["biometric_verification"]["roc_auc"],
        "tar_at_1_percent_far": eval_resnet["biometric_verification"]["tar_at_far_1_percent"],
        "latency_ms": eval_resnet["performance"]["latency_ms_per_pair"],
        "throughput_pairs_sec": eval_resnet["performance"]["throughput_pairs_per_sec"],
        "parameters": eval_resnet["performance"]["total_parameters"],
    })
    tf.keras.backend.clear_session()

    # ------------------ MODEL 3: MobileNetV3 Siamese ------------------
    print("\n--- Model 3: MobileNetV3 Siamese ---")
    mobilenet_model, _ = build_mobilenet_siamese_network()
    mobilenet_model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss=contrastive_loss(1.0))
    mobilenet_model.fit([tx1, tx2], ty, validation_data=([vx1, vx2], vy), batch_size=32, epochs=1, verbose=2)

    eval_mob = evaluate_verification(mobilenet_model, te_p1, te_p2, te_y, preprocessor=preprocessor)
    comparison_results.append({
        "model_name": "MobileNetV3 Siamese",
        "accuracy": eval_mob["classification"]["accuracy"],
        "eer": eval_mob["biometric_verification"]["eer"],
        "roc_auc": eval_mob["biometric_verification"]["roc_auc"],
        "tar_at_1_percent_far": eval_mob["biometric_verification"]["tar_at_far_1_percent"],
        "latency_ms": eval_mob["performance"]["latency_ms_per_pair"],
        "throughput_pairs_sec": eval_mob["performance"]["throughput_pairs_per_sec"],
        "parameters": eval_mob["performance"]["total_parameters"],
    })
    tf.keras.backend.clear_session()

    # ------------------ MODEL 4: Classical HOG + Distance Baseline ------------------
    print("\n--- Model 4: Classical HOG Baseline ---")
    hog_verifier = HOGSVMVerifier()
    t0_hog = time.time()
    feats1 = hog_verifier.hog_extractor.extract_batch(te_p1, preprocessor)
    feats2 = hog_verifier.hog_extractor.extract_batch(te_p2, preprocessor)
    hog_dists = hog_verifier.predict_distances(feats1, feats2)
    hog_time = time.time() - t0_hog

    from src.evaluation.metrics import compute_biometric_verification_metrics, compute_classification_metrics
    hog_verif = compute_biometric_verification_metrics(te_y, hog_dists)
    hog_class = compute_classification_metrics(te_y, hog_dists, hog_verif["eer_threshold_distance"])

    comparison_results.append({
        "model_name": "HOG Feature Baseline",
        "accuracy": hog_class["accuracy"],
        "eer": hog_verif["eer"],
        "roc_auc": hog_verif["roc_auc"],
        "tar_at_1_percent_far": hog_verif["tar_at_far_1_percent"],
        "latency_ms": float((hog_time / len(te_y)) * 1000.0),
        "throughput_pairs_sec": float(len(te_y) / hog_time),
        "parameters": 0,
    })

    # Save and summarize
    comp_file = REPORTS_DIR / "model_benchmark_comparisons.json"
    with open(comp_file, "w") as f:
        json.dump(comparison_results, f, indent=2)
    print(f"\nSaved Benchmark Comparisons JSON: {comp_file}")

    # Generate visualization
    plot_model_comparisons(comparison_results, PLOTS_DIR)

    # Print summary table
    print("\n" + "=" * 90)
    print(f"{'Model':<25} | {'Accuracy':<10} | {'EER':<10} | {'ROC-AUC':<10} | {'Latency':<12} | {'Params':<10}")
    print("-" * 90)
    for r in comparison_results:
        print(f"{r['model_name']:<25} | {r['accuracy']*100:>8.2f}% | {r['eer']*100:>8.2f}% | {r['roc_auc']:>10.4f} | {r['latency_ms']:>8.2f} ms | {r['parameters']:>10,}")
    print("=" * 90)
    print("Phase 6 Benchmark Comparisons Completed Successfully.")


if __name__ == "__main__":
    main()
