"""
Kosha Labs Biometric Fingerprint Inference Engine.
High-level interface for loading models, extracting 128-D embeddings,
and performing 1:1 verification and 1:N biometric identification.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np

import tensorflow as tf
from ml.preprocessing.pipeline import FingerprintPreprocessor
from ml.models.siamese_cnn import build_base_cnn, build_siamese_network
from ml.models.losses import contrastive_loss, EuclideanDistanceLayer


class BiometricInferenceEngine:
    """Production ML Biometric Inference Engine for Fingerprint Recognition."""

    def __init__(
        self,
        weights_path: Optional[str] = None,
        thresholds_path: Optional[str] = None,
        input_shape: Tuple[int, int, int] = (128, 128, 1),
        embedding_dim: int = 128
    ):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.weights_path = weights_path or os.path.join(base_dir, "checkpoints", "siamese_cnn_final.weights.h5")
        self.thresholds_path = thresholds_path or os.path.join(base_dir, "checkpoints", "calibrated_thresholds.json")
        self.input_shape = input_shape
        self.embedding_dim = embedding_dim

        self.preprocessor = FingerprintPreprocessor(target_size=(input_shape[0], input_shape[1]))
        self.feature_extractor: Optional[tf.keras.Model] = None
        self.calibrated_thresholds: Dict[str, float] = self._load_thresholds()

        self._initialize_model()

    def _load_thresholds(self) -> Dict[str, float]:
        """Loads calibrated operating thresholds."""
        default_thresholds = {
            "strict_far_0_1_percent": 0.0150,
            "standard_far_1_percent": 0.0200,
            "eer_threshold": 0.0235,
            "duplicate_prevention_threshold": 0.0200
        }
        if os.path.exists(self.thresholds_path):
            try:
                with open(self.thresholds_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    return {**default_thresholds, **loaded}
            except Exception:
                pass
        return default_thresholds

    def _initialize_model(self) -> None:
        """Instantiates base CNN and loads trained weights."""
        if os.path.exists(self.weights_path):
            siamese_net, base_net = build_siamese_network(input_shape=self.input_shape, embedding_dim=self.embedding_dim)
            siamese_net.load_weights(self.weights_path)
            self.feature_extractor = base_net
            print(f"[BiometricInferenceEngine] Successfully loaded trained weights from {self.weights_path}")
        else:
            self.feature_extractor = build_base_cnn(input_shape=self.input_shape, embedding_dim=self.embedding_dim)
            print(f"[BiometricInferenceEngine] Warning: Checkpoint not found at {self.weights_path}. Model uninitialized.")

    def extract_embedding(self, image_input: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """
        Extracts 128-D L2-normalized embedding vector from a fingerprint image.
        
        Args:
            image_input: Filepath string, raw image bytes, or numpy array.
            
        Returns:
            np.ndarray of shape (128,) with ||z||₂ = 1.0.
        """
        # Load and validate quality
        raw_gray = self.preprocessor.load_image(image_input)
        is_valid, quality_score, reason = self.preprocessor.validate_quality(raw_gray)
        if not is_valid:
            raise ValueError(f"Fingerprint image failed quality validation: {reason}")

        processed_img = self.preprocessor.process_image(raw_gray)
        batch_tensor = np.expand_dims(processed_img, axis=0)
        embedding = self.feature_extractor(batch_tensor, training=False).numpy()[0]
        return embedding

    def compute_distance(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Computes Euclidean distance between two embeddings."""
        return float(np.linalg.norm(emb1 - emb2))

    def verify(
        self,
        image_a: Union[str, bytes, np.ndarray],
        image_b: Union[str, bytes, np.ndarray],
        security_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        1:1 Biometric Verification between two fingerprint captures.
        
        Args:
            image_a: Probe fingerprint capture A.
            image_b: Probe fingerprint capture B.
            security_level: 'strict', 'standard', or 'eer'.
            
        Returns:
            Dictionary with distance, threshold, is_match, and confidence score.
        """
        emb_a = self.extract_embedding(image_a)
        emb_b = self.extract_embedding(image_b)
        dist = self.compute_distance(emb_a, emb_b)

        if security_level == "strict":
            thresh = self.calibrated_thresholds["strict_far_0_1_percent"]
        elif security_level == "eer":
            thresh = self.calibrated_thresholds["eer_threshold"]
        else:
            thresh = self.calibrated_thresholds["standard_far_1_percent"]

        is_match = bool(dist <= thresh)
        confidence = float(max(0.0, min(1.0, 1.0 - (dist / (thresh * 2.0)))))

        return {
            "is_match": is_match,
            "euclidean_distance": round(dist, 6),
            "threshold_used": thresh,
            "security_level": security_level,
            "confidence_score": round(confidence, 4)
        }
