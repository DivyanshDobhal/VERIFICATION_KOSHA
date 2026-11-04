"""
Biometric fingerprint image preprocessing pipeline.
Implements grayscale conversion, resizing, CLAHE contrast enhancement,
bilateral noise reduction with ridge preservation, normalization, and quality validation.
"""

from typing import Tuple, Union, Optional
import numpy as np
import cv2
import tensorflow as tf


class FingerprintPreprocessor:
    """
    Reusable, production-grade fingerprint preprocessing pipeline.
    Preserves minutiae and ridge topology while eliminating noise and illumination artifacts.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = (128, 128),
        clahe_clip_limit: float = 2.0,
        clahe_tile_grid: Tuple[int, int] = (8, 8),
        apply_denoise: bool = True,
        min_quality_laplacian: float = 10.0,
    ):
        self.target_size = target_size
        self.clahe = cv2.createCLAHE(
            clipLimit=clahe_clip_limit, tileGridSize=clahe_tile_grid
        )
        self.apply_denoise = apply_denoise
        self.min_quality_laplacian = min_quality_laplacian

    def load_image(self, image_input: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """
        Loads image from file path, raw bytes (API upload), or existing numpy array.
        Returns uint8 grayscale image.
        """
        if isinstance(image_input, (str, bytes)):
            if isinstance(image_input, str):
                img = cv2.imread(image_input, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    raise ValueError(f"Failed to load image from path: {image_input}")
                return img
            else:
                # Raw bytes from multipart upload
                nparr = np.frombuffer(image_input, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    raise ValueError("Failed to decode uploaded image bytes.")
                return img
        elif isinstance(image_input, np.ndarray):
            if len(image_input.shape) == 3:
                if image_input.shape[2] == 3:
                    return cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
                elif image_input.shape[2] == 1:
                    return image_input[:, :, 0]
            return image_input
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

    def validate_quality(self, img_gray: np.ndarray) -> Tuple[bool, float, str]:
        """
        Validates if the fingerprint image has sufficient ridge contrast and sharpness.
        """
        if img_gray is None or img_gray.size == 0:
            return False, 0.0, "Empty image"

        lap_var = float(cv2.Laplacian(img_gray, cv2.CV_64F).var())
        if lap_var < self.min_quality_laplacian:
            return False, lap_var, f"Low quality/blurred image (Laplacian variance {lap_var:.1f} < {self.min_quality_laplacian})"

        # Check for nearly blank / saturated images
        mean_val = float(np.mean(img_gray))
        if mean_val < 5.0 or mean_val > 250.0:
            return False, lap_var, f"Extreme illumination / saturated image (mean intensity {mean_val:.1f})"

        return True, lap_var, "Valid quality"

    def process_image(
        self,
        image_input: Union[str, bytes, np.ndarray],
        return_tensor: bool = False,
    ) -> Union[np.ndarray, tf.Tensor]:
        """
        Full preprocessing chain:
        1. Load & Grayscale
        2. Bilateral filtering for ridge preservation & noise suppression
        3. CLAHE adaptive contrast enhancement
        4. Resize to target dimension (128, 128)
        5. Pixel normalization to [0.0, 1.0] float32
        6. Expand dimensions to (H, W, 1)
        """
        img = self.load_image(image_input)

        # 1. Bilateral filtering: smooths sensor noise while preserving sharp ridge boundaries
        if self.apply_denoise:
            # d=5, sigmaColor=50, sigmaSpace=50
            denoised = cv2.bilateralFilter(img, d=5, sigmaColor=50, sigmaSpace=50)
        else:
            denoised = img

        # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        enhanced = self.clahe.apply(denoised)

        # 3. Resizing
        h, w = self.target_size
        if enhanced.shape != (h, w):
            resized = cv2.resize(enhanced, (w, h), interpolation=cv2.INTER_AREA)
        else:
            resized = enhanced

        # 4. Pixel Normalization [0, 1]
        normalized = resized.astype(np.float32) / 255.0

        # 5. Expand to channel dimension (H, W, 1)
        expanded = np.expand_dims(normalized, axis=-1)

        if return_tensor:
            return tf.convert_to_tensor(expanded, dtype=tf.float32)

        return expanded


# Global default preprocessor instance
default_preprocessor = FingerprintPreprocessor()

