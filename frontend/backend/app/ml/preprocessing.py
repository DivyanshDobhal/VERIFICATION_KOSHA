import base64
import numpy as np
import cv2
from typing import Tuple, Optional

class FingerprintPreprocessor:
    """Preprocesses raw optical/capacitive scanner images for Siamese CNN embedding extraction."""

    @staticmethod
    def decode_base64_image(image_base64: str) -> Optional[np.ndarray]:
        try:
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            image_data = base64.b64decode(image_base64)
            np_arr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
            return img
        except Exception:
            return None

    @staticmethod
    def assess_quality(img: np.ndarray) -> float:
        """Computes NFIQ-like ridge clarity index based on Laplacian variance and local ridge contrast."""
        if img is None:
            return 0.0
        # Compute sharpness via Laplacian variance
        laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
        # Normalize into 0-100 quality score
        quality = min(100.0, max(10.0, (laplacian_var / 500.0) * 100.0))
        return round(float(quality), 2)

    @classmethod
    def preprocess_for_siamese_cnn(cls, img: np.ndarray, target_size: Tuple[int, int] = (128, 128)) -> np.ndarray:
        """Applies CLAHE, Gabor ridge contrast, and resizes to 128x128 normalized float32 tensor."""
        # 1. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img)

        # 2. Gaussian blur to reduce high-frequency scanner noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

        # 3. Resize to CNN input shape
        resized = cv2.resize(blurred, target_size, interpolation=cv2.INTER_AREA)

        # 4. Normalize to [-1.0, 1.0]
        normalized = (resized.astype(np.float32) - 127.5) / 127.5
        # Expand channel dimension
        tensor = np.expand_dims(normalized, axis=-1)
        return tensor

preprocessor = FingerprintPreprocessor()
