"""
Kosha Labs Biometric Fingerprint Recognition - Machine Learning Package (ml).
Strictly biometric fingerprint recognition, feature extraction, and identity verification.
"""

from ml.preprocessing.pipeline import FingerprintPreprocessor
from ml.preprocessing.augmentation import BiometricAugmentor
from ml.models.siamese_cnn import build_base_cnn, build_siamese_network
from ml.models.losses import contrastive_loss, EuclideanDistanceLayer
from ml.engine import BiometricInferenceEngine

__all__ = [
    "FingerprintPreprocessor",
    "BiometricAugmentor",
    "build_base_cnn",
    "build_siamese_network",
    "contrastive_loss",
    "EuclideanDistanceLayer",
    "BiometricInferenceEngine"
]

