"""
Stratified Hyperparameter Optimization for Siamese Fingerprint Verification.
Conducts systematic parameter exploration across learning rates, margins,
embedding dimensions, and dropout rates using validation EER objective.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import time
import pandas as pd
import numpy as np
import tensorflow as tf

from src.models.siamese_cnn import build_siamese_network
from src.models.losses import contrastive_loss
from src.data.pair_generator import FingerprintPairGenerator, load_pair_arrays
from src.evaluation.evaluator import evaluate_verification
from src.preprocessing.pipeline import FingerprintPreprocessor
from src.preprocessing.augmentation import BiometricAugmentor


class HyperparameterTuner:
    """
    Explores hyperparameter configurations and records validation EER and ROC-AUC.
    """

    def __init__(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        output_dir: Path,
        seed: int = 42,
    ):
        self.train_df = train_df
        self.val_df = val_df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.seed = seed
        self.preprocessor = FingerprintPreprocessor()

    def run_tuning(self, configurations: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Executes hyperparameter trials.
        """
        if configurations is None:
            configurations = [
                {"name": "Baseline_Default", "lr": 1e-4, "margin": 1.0, "emb_dim": 128, "dropout": 0.3, "batch_size": 32, "opt": "adam"},
                {"name": "Higher_LR_Margin1.2", "lr": 3e-4, "margin": 1.2, "emb_dim": 128, "dropout": 0.3, "batch_size": 32, "opt": "adam"},
                {"name": "Compact_Emb64", "lr": 1e-4, "margin": 1.0, "emb_dim": 64, "dropout": 0.2, "batch_size": 32, "opt": "adam"},
                {"name": "Deep_Emb256_Drop0.4", "lr": 1e-4, "margin": 1.0, "emb_dim": 256, "dropout": 0.4, "batch_size": 32, "opt": "adam"},
                {"name": "Margin0.8_RMSprop", "lr": 1e-4, "margin": 0.8, "emb_dim": 128, "dropout": 0.3, "batch_size": 32, "opt": "rmsprop"},
            ]

        # Prepare validation pairs once for consistent evaluation
        val_factory = FingerprintPairGenerator(self.val_df, seed=self.seed)
        v_p1, v_p2, v_y = val_factory.generate_pairs(num_pairs=150)
        (vx1, vx2), vy = load_pair_arrays(v_p1, v_p2, v_y, preprocessor=self.preprocessor)

        train_factory = FingerprintPairGenerator(self.train_df, seed=self.seed)
        t_p1, t_p2, t_y = train_factory.generate_pairs(num_pairs=300)
        (tx1, tx2), ty = load_pair_arrays(t_p1, t_p2, t_y, preprocessor=self.preprocessor)

        trial_results = []
        print(f"Beginning Hyperparameter Search across {len(configurations)} trials...")

        for trial_idx, config in enumerate(configurations, start=1):
            print(f"\nTrial {trial_idx}/{len(configurations)}: {config['name']} -> {config}")
            t0 = time.time()

            # Build model with trial hyperparameters
            siamese_model, feature_extractor = build_siamese_network(
                embedding_dim=config["emb_dim"],
                dropout_rate=config["dropout"],
            )

            if config["opt"] == "adam":
                optimizer = tf.keras.optimizers.Adam(learning_rate=config["lr"])
            else:
                optimizer = tf.keras.optimizers.RMSprop(learning_rate=config["lr"])

            siamese_model.compile(
                optimizer=optimizer,
                loss=contrastive_loss(margin=config["margin"]),
            )

            # Quick training (2 epochs for tuning exploration)
            siamese_model.fit(
                [tx1, tx2],
                ty,
                validation_data=([vx1, vx2], vy),
                batch_size=config["batch_size"],
                epochs=2,
                verbose=0,
            )
            trial_time = time.time() - t0

            # Evaluate on validation pairs
            eval_metrics = evaluate_verification(
                model=siamese_model,
                img1_paths=v_p1,
                img2_paths=v_p2,
                labels=v_y,
                preprocessor=self.preprocessor,
            )

            record = {
                "trial": trial_idx,
                "config_name": config["name"],
                "params": config,
                "val_eer": float(eval_metrics["biometric_verification"]["eer"]),
                "val_roc_auc": float(eval_metrics["biometric_verification"]["roc_auc"]),
                "val_accuracy": float(eval_metrics["classification"]["accuracy"]),
                "val_tar_at_1_percent_far": float(eval_metrics["biometric_verification"]["tar_at_far_1_percent"]),
                "trial_time_seconds": float(trial_time),
            }
            trial_results.append(record)
            print(f"Trial {trial_idx} Result -> Val EER: {record['val_eer']:.4f} | ROC-AUC: {record['val_roc_auc']:.4f} | Acc: {record['val_accuracy']:.4f}")
            tf.keras.backend.clear_session()

        # Sort trials by validation EER ascending
        trial_results.sort(key=lambda x: x["val_eer"])
        best_trial = trial_results[0]

        summary = {
            "num_trials": len(configurations),
            "best_trial": best_trial,
            "all_trials": trial_results,
        }

        # Save results
        out_file = self.output_dir / "hyperparameter_tuning_results.json"
        with open(out_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nHyperparameter Tuning Complete! Best Config: {best_trial['config_name']} (EER={best_trial['val_eer']:.4f})")
        print(f"Results saved to: {out_file}")

        return summary



