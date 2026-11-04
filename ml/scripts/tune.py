"""
Execution script for Phase 7: Stratified Hyperparameter Optimization.
Runs trials across learning rates, margins, embedding sizes, dropouts, and optimizers.
"""

import tensorflow as tf
import sys
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import REPORTS_DIR
from ml.training.tuner import HyperparameterTuner


def main():
    print("=" * 70)
    print("PHASE 7: Stratified Hyperparameter Optimization")
    print("=" * 70)

    split_dir = REPORTS_DIR / "splits"
    train_csv = split_dir / "protocol_a_train.csv"
    val_csv = split_dir / "protocol_a_val.csv"

    if not train_csv.exists():
        print("Dataset splits not found. Run Phase 3 first.")
        sys.exit(1)

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)

    tuner = HyperparameterTuner(
        train_df=train_df,
        val_df=val_df,
        output_dir=REPORTS_DIR,
        seed=42,
    )

    tuning_results = tuner.run_tuning()

    print("\n" + "=" * 80)
    print("HYPERPARAMETER TUNING SUMMARY TABLE:")
    print(f"{'Config Name':<25} | {'EER':<10} | {'ROC-AUC':<10} | {'Accuracy':<10} | {'Trial Time':<10}")
    print("-" * 80)
    for trial in tuning_results["all_trials"]:
        print(f"{trial['config_name']:<25} | {trial['val_eer']*100:>8.2f}% | {trial['val_roc_auc']:>10.4f} | {trial['val_accuracy']*100:>8.2f}% | {trial['trial_time_seconds']:>8.1f}s")
    print("=" * 80)
    print(f"Optimal Configuration: {tuning_results['best_trial']['config_name']}")
    print("Phase 7 Completed Successfully.")


if __name__ == "__main__":
    main()
