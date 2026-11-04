"""
Threshold optimization engine for biometric verification.
Calculates and persists calibrated decision thresholds:
- Equal Error Rate (EER) threshold: balanced trade-off
- Strict Security threshold: calibrated at FAR <= 0.1%
- Standard Operating threshold: calibrated at FAR <= 1.0%
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import numpy as np


class ThresholdOptimizer:
    """
    Calibrates operational decision thresholds on validation verification sets.
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
    ):
        self.config_path = config_path or Path("./checkpoints/calibrated_thresholds.json")
        self.thresholds = {
            "eer_threshold": 0.85,
            "strict_far_01_threshold": 0.65,
            "standard_far_1_threshold": 0.75,
            "duplicate_prevention_threshold": 0.70,
        }
        self.load()

    def calibrate(
        self,
        y_true: np.ndarray,
        distances: np.ndarray,
        save: bool = True,
    ) -> Dict[str, float]:
        """
        Calibrates thresholds using true validation labels and distances.
        """
        from sklearn.metrics import roc_curve
        scores = -distances
        fpr, tpr, roc_thresholds = roc_curve(y_true.astype(int), scores)
        fnr = 1.0 - tpr

        # 1. EER threshold
        diff = np.abs(fpr - fnr)
        eer_idx = np.argmin(diff)
        eer_thresh = float(-roc_thresholds[eer_idx])

        # 2. FAR <= 0.1% (0.001)
        idx_01 = np.where(fpr <= 0.001)[0]
        thresh_01 = float(-roc_thresholds[idx_01[-1]]) if len(idx_01) > 0 else float(eer_thresh * 0.75)

        # 3. FAR <= 1.0% (0.01)
        idx_1 = np.where(fpr <= 0.01)[0]
        thresh_1 = float(-roc_thresholds[idx_1[-1]]) if len(idx_1) > 0 else float(eer_thresh * 0.88)

        self.thresholds = {
            "eer_threshold": eer_thresh,
            "strict_far_01_threshold": thresh_01,
            "standard_far_1_threshold": thresh_1,
            "duplicate_prevention_threshold": float(min(thresh_1, eer_thresh)),
        }

        if save:
            self.save()

        return self.thresholds

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.thresholds, f, indent=2)

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.thresholds.update(data)
            except Exception:
                pass

