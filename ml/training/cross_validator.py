"""
5-Fold Stratified Group Cross-Validation Engine.
Guarantees source-group containment and zero data leakage across folds.
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
import tensorflow as tf

from ml.models.siamese_cnn import build_siamese_network
from ml.data.pair_generator import FingerprintPairGenerator, load_pair_arrays
from ml.training.trainer import SiameseTrainer
from ml.evaluation.evaluator import evaluate_verification, compute_95_ci
from ml.preprocessing.pipeline import FingerprintPreprocessor
from ml.preprocessing.augmentation import BiometricAugmentor


class StratifiedGroupCrossValidator:
    """
    Executes 5-Fold Cross Validation where groups are original source fingerprint groups.
    """

    def __init__(
        self,
        df_train_pool: pd.DataFrame,
        n_splits: int = 5,
        epochs_per_fold: int = 15,
        batch_size: int = 32,
        pairs_per_fold_train: int = 4000,
        pairs_per_fold_val: int = 1000,
        checkpoint_dir: Optional[Path] = None,
        seed: int = 42,
    ):
        self.df = df_train_pool.reset_index(drop=True)
        self.n_splits = n_splits
        self.epochs = epochs_per_fold
        self.batch_size = batch_size
        self.pairs_train = pairs_per_fold_train
        self.pairs_val = pairs_per_fold_val
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else Path("./checkpoints")
        self.seed = seed
        self.preprocessor = FingerprintPreprocessor()
        self.augmentor = BiometricAugmentor(seed=seed)

    def run_cross_validation(self) -> Dict[str, Any]:
        """
        Executes full 5-fold cross validation.
        """
        sgkf = StratifiedGroupKFold(n_splits=self.n_splits, shuffle=True, random_state=self.seed)

        groups = self.df["source_finger_group"].values
        # Stratify by subject_id
        y = self.df["subject_id"].values
        X = np.arange(len(self.df))

        fold_results: List[Dict[str, Any]] = []

        print(f"\nInitiating {self.n_splits}-Fold Stratified Group Cross-Validation...")
        for fold, (train_idx, val_idx) in enumerate(sgkf.split(X, y, groups), start=1):
            print(f"\n==================== FOLD {fold}/{self.n_splits} ====================")
            train_fold_df = self.df.iloc[train_idx].copy()
            val_fold_df = self.df.iloc[val_idx].copy()

            # Verify no group overlap
            overlap = set(train_fold_df["source_finger_group"]).intersection(
                set(val_fold_df["source_finger_group"])
            )
            assert len(overlap) == 0, f"Leakage detected in fold {fold}: {len(overlap)} overlapping groups!"

            print(f"Fold {fold} Train: {len(train_fold_df)} imgs ({train_fold_df['source_finger_group'].nunique()} groups)")
            print(f"Fold {fold} Val:   {len(val_fold_df)} imgs ({val_fold_df['source_finger_group'].nunique()} groups)")

            # Generate pairs independently
            train_gen_factory = FingerprintPairGenerator(train_fold_df, seed=self.seed + fold)
            val_gen_factory = FingerprintPairGenerator(val_fold_df, seed=self.seed + fold * 10)

            t_p1, t_p2, t_y = train_gen_factory.generate_pairs(num_pairs=self.pairs_train)
            v_p1, v_p2, v_y = val_gen_factory.generate_pairs(num_pairs=self.pairs_val)

            train_arrays = load_pair_arrays(
                t_p1, t_p2, t_y,
                preprocessor=self.preprocessor,
                augmentor=self.augmentor,
            )
            val_arrays = load_pair_arrays(
                v_p1, v_p2, v_y,
                preprocessor=self.preprocessor,
                augmentor=None,
            )

            # Build model instance for this fold
            siamese_model, feature_extractor = build_siamese_network()
            trainer = SiameseTrainer(
                siamese_model=siamese_model,
                feature_extractor=feature_extractor,
                checkpoint_dir=self.checkpoint_dir,
            )

            hist, ckpt_path = trainer.train(
                train_data=train_arrays,
                val_data=val_arrays,
                epochs=self.epochs,
                batch_size=self.batch_size,
                fold_id=fold,
            )

            # Evaluate fold on validation pairs
            eval_metrics = evaluate_verification(
                model=siamese_model,
                img1_paths=v_p1,
                img2_paths=v_p2,
                labels=v_y,
                preprocessor=self.preprocessor,
            )

            fold_record = {
                "fold": fold,
                "best_epoch": hist["best_epoch"],
                "best_val_loss": hist["best_val_loss"],
                "training_time_seconds": hist["training_time_seconds"],
                "checkpoint_path": str(ckpt_path),
                "accuracy": eval_metrics["classification"]["accuracy"],
                "precision": eval_metrics["classification"]["precision"],
                "recall": eval_metrics["classification"]["recall"],
                "f1_score": eval_metrics["classification"]["f1_score"],
                "specificity": eval_metrics["classification"]["specificity"],
                "mcc": eval_metrics["classification"]["matthews_corrcoef"],
                "eer": eval_metrics["biometric_verification"]["eer"],
                "eer_threshold": eval_metrics["biometric_verification"]["eer_threshold_distance"],
                "roc_auc": eval_metrics["biometric_verification"]["roc_auc"],
                "pr_auc": eval_metrics["biometric_verification"]["pr_auc"],
                "tar_at_far_1_percent": eval_metrics["biometric_verification"]["tar_at_far_1_percent"],
                "latency_ms": eval_metrics["performance"]["latency_ms_per_pair"],
            }
            fold_results.append(fold_record)
            print(f"Fold {fold} Complete -> Val EER: {fold_record['eer']:.4f} | ROC-AUC: {fold_record['roc_auc']:.4f} | Acc: {fold_record['accuracy']:.4f}")

            # Clear keras session to free memory between folds
            tf.keras.backend.clear_session()

        # Compute summary statistics across all folds with 95% Confidence Intervals
        metric_keys = [
            "accuracy", "precision", "recall", "f1_score", "specificity",
            "mcc", "eer", "roc_auc", "pr_auc", "tar_at_far_1_percent", "best_val_loss"
        ]
        aggregated_metrics = {}
        for k in metric_keys:
            vals = [f[k] for f in fold_results]
            aggregated_metrics[k] = compute_95_ci(vals)

        cv_summary = {
            "n_splits": self.n_splits,
            "fold_results": fold_results,
            "aggregate_statistics_with_95_ci": aggregated_metrics,
        }

        return cv_summary


