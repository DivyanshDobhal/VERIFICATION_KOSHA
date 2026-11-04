"""
Execution script for Phase 4 & Phase 5:
- 5-Fold Stratified Group Cross-Validation
- Primary Siamese CNN training with shared weights & contrastive loss
- 95% Confidence Intervals aggregation
- Final untouched test evaluation
"""

import tensorflow as tf
import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import REPORTS_DIR, CHECKPOINTS_DIR, PLOTS_DIR
from ml.models.siamese_cnn import build_siamese_network
from ml.data.pair_generator import FingerprintPairGenerator, load_pair_arrays
from ml.training.trainer import SiameseTrainer
from ml.training.cross_validator import StratifiedGroupCrossValidator
from ml.evaluation.evaluator import evaluate_verification, compute_95_ci
from ml.visualization.plot_curves import (
    plot_learning_curves,
    plot_roc_and_pr_curves,
    plot_confusion_matrix_heatmap,
    plot_cross_validation_folds,
)
from ml.preprocessing.pipeline import FingerprintPreprocessor
from ml.preprocessing.augmentation import BiometricAugmentor


def main():
    print("=" * 70)
    print("PHASE 4 & 5: 5-Fold Stratified Group Cross-Validation & Siamese CNN")
    print("=" * 70)

    split_dir = REPORTS_DIR / "splits"
    train_csv = split_dir / "protocol_a_train.csv"
    val_csv = split_dir / "protocol_a_val.csv"
    test_csv = split_dir / "protocol_a_test.csv"

    if not train_csv.exists():
        print("Protocol splits not found. Run Phase 3 first.")
        sys.exit(1)

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)
    test_df = pd.read_csv(test_csv)

    print(f"Loaded Protocol A Pools: Train={len(train_df):,}, Val={len(val_df):,}, Test={len(test_df):,}")

    # Step 1: Execute 5-Fold Stratified Group Cross-Validation
    cv_engine = StratifiedGroupCrossValidator(
        df_train_pool=train_df,
        n_splits=5,
        epochs_per_fold=2,
        batch_size=32,
        pairs_per_fold_train=400,
        pairs_per_fold_val=150,
        checkpoint_dir=CHECKPOINTS_DIR,
        seed=42,
    )

    cv_summary = cv_engine.run_cross_validation()

    # Save CV results
    cv_report_path = REPORTS_DIR / "cross_validation_5fold_results.json"
    with open(cv_report_path, "w") as f:
        json.dump(cv_summary, f, indent=2)
    print(f"\nSaved 5-Fold CV Report: {cv_report_path}")

    # Plot CV fold comparison
    plot_cross_validation_folds(cv_summary, PLOTS_DIR)

    # Step 2: Train Primary Siamese CNN Model on Full Training Set
    print("\n==================== TRAINING PRIMARY SIAMESE CNN ====================")
    preprocessor = FingerprintPreprocessor()
    augmentor = BiometricAugmentor(seed=42)

    train_factory = FingerprintPairGenerator(train_df, seed=42)
    val_factory = FingerprintPairGenerator(val_df, seed=100)

    train_p1, train_p2, train_y = train_factory.generate_pairs(num_pairs=800)
    val_p1, val_p2, val_y = val_factory.generate_pairs(num_pairs=200)

    train_arrays = load_pair_arrays(train_p1, train_p2, train_y, preprocessor=preprocessor, augmentor=augmentor)
    val_arrays = load_pair_arrays(val_p1, val_p2, val_y, preprocessor=preprocessor, augmentor=None)

    siamese_model, feature_extractor = build_siamese_network(embedding_dim=128, dropout_rate=0.3)
    trainer = SiameseTrainer(
        siamese_model=siamese_model,
        feature_extractor=feature_extractor,
        checkpoint_dir=CHECKPOINTS_DIR,
    )

    history, best_ckpt = trainer.train(train_arrays, val_arrays, epochs=4, batch_size=32)

    # Save final model weights
    final_weights_path = CHECKPOINTS_DIR / "siamese_cnn_final.weights.h5"
    siamese_model.save_weights(str(final_weights_path))
    print(f"Saved Primary Model Weights: {final_weights_path}")

    # Plot learning curves
    plot_learning_curves(history, PLOTS_DIR, title_suffix="Primary Siamese CNN")

    # Step 3: Final Untouched Test Set Evaluation
    print("\n==================== UNTOUCHED TEST SET EVALUATION ====================")
    test_factory = FingerprintPairGenerator(test_df, seed=999)
    test_p1, test_p2, test_y = test_factory.generate_pairs(num_pairs=400)

    test_eval = evaluate_verification(
        model=siamese_model,
        img1_paths=test_p1,
        img2_paths=test_p2,
        labels=test_y,
        preprocessor=preprocessor,
    )

    eer = test_eval["biometric_verification"]["eer"]
    roc_auc = test_eval["biometric_verification"]["roc_auc"]
    acc = test_eval["classification"]["accuracy"]
    tar_1 = test_eval["biometric_verification"]["tar_at_far_1_percent"]

    print(f"Final Test Set Evaluation Complete:")
    print(f"  - Accuracy:              {acc*100:.2f}%")
    print(f"  - Equal Error Rate (EER): {eer*100:.2f}%")
    print(f"  - ROC-AUC:               {roc_auc:.4f}")
    print(f"  - TAR @ FAR=1.0%:        {tar_1*100:.2f}%")
    print(f"  - Inference Latency:     {test_eval['performance']['latency_ms_per_pair']:.2f} ms/pair")

    # Save test curves and confusion matrix
    plot_roc_and_pr_curves(test_eval, PLOTS_DIR, model_name="Siamese CNN Test")
    plot_confusion_matrix_heatmap(test_eval["classification"], PLOTS_DIR, model_name="Siamese CNN Test")

    # Save test report
    test_report_file = REPORTS_DIR / "siamese_cnn_test_metrics.json"
    clean_test_eval = {
        "num_pairs_evaluated": test_eval["num_pairs_evaluated"],
        "performance": test_eval["performance"],
        "biometric_verification": {
            k: v for k, v in test_eval["biometric_verification"].items() if k != "curve_data"
        },
        "classification": test_eval["classification"],
    }
    with open(test_report_file, "w") as f:
        json.dump(clean_test_eval, f, indent=2)
    print(f"Saved Test Metrics: {test_report_file}")
    print("\nPhase 4 & 5 Completed Successfully.")


if __name__ == "__main__":
    main()
