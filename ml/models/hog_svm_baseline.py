"""
Comparison Model 4: Classical Fingerprint Baseline with HOG & SVM / Metric Distance.
Extracts Histogram of Oriented Gradients (HOG) to model ridge orientations,
and performs pair verification via distance / Support Vector Machine.
"""

from typing import List, Tuple
import numpy as np
import cv2
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from ml.preprocessing.pipeline import FingerprintPreprocessor


class HOGFeatureExtractor:
    """
    Computes Histogram of Oriented Gradients for fingerprint ridge analysis.
    """

    def __init__(
        self,
        win_size: Tuple[int, int] = (128, 128),
        block_size: Tuple[int, int] = (16, 16),
        block_stride: Tuple[int, int] = (8, 8),
        cell_size: Tuple[int, int] = (8, 8),
        nbins: int = 9,
    ):
        self.win_size = win_size
        self.hog = cv2.HOGDescriptor(
            _winSize=win_size,
            _blockSize=block_size,
            _blockStride=block_stride,
            _cellSize=cell_size,
            _nbins=nbins,
        )
        self.scaler = StandardScaler()
        self.is_fitted = False

    def extract(self, img: np.ndarray) -> np.ndarray:
        """
        Extracts HOG descriptor from a 128x128 grayscale image.
        """
        if img.dtype != np.uint8:
            img_uint8 = (img * 255.0).clip(0, 255).astype(np.uint8)
        else:
            img_uint8 = img

        if len(img_uint8.shape) == 3:
            img_uint8 = img_uint8[:, :, 0]

        feat = self.hog.compute(img_uint8)
        if feat is None:
            return np.zeros((1764,), dtype=np.float32)
        return feat.flatten()

    def extract_batch(self, image_paths: List[str], preprocessor: FingerprintPreprocessor) -> np.ndarray:
        """
        Extracts HOG descriptors for a batch of images.
        """
        features = []
        for p in image_paths:
            img = preprocessor.process_image(p)
            feat = self.extract(img)
            features.append(feat)
        return np.array(features, dtype=np.float32)


class HOGSVMVerifier:
    """
    Classical fingerprint verifier using HOG difference vector and Linear SVM / L2 Distance.
    """

    def __init__(self):
        self.hog_extractor = HOGFeatureExtractor()
        self.svm = LinearSVC(C=1.0, max_iter=2000, random_state=42)

    def fit(self, feats1: np.ndarray, feats2: np.ndarray, labels: np.ndarray):
        """
        Trains Linear SVM on absolute difference vectors |f1 - f2|.
        """
        diff = np.abs(feats1 - feats2)
        diff_scaled = self.hog_extractor.scaler.fit_transform(diff)
        self.svm.fit(diff_scaled, labels)
        self.hog_extractor.is_fitted = True

    def predict_distances(self, feats1: np.ndarray, feats2: np.ndarray) -> np.ndarray:
        """
        Returns normalized Euclidean distance or negative SVM decision function.
        """
        diff = np.abs(feats1 - feats2)
        # Normalize features
        norm1 = feats1 / (np.linalg.norm(feats1, axis=1, keepdims=True) + 1e-7)
        norm2 = feats2 / (np.linalg.norm(feats2, axis=1, keepdims=True) + 1e-7)
        distances = np.linalg.norm(norm1 - norm2, axis=1)
        return distances

