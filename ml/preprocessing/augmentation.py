"""
Biometric-preserving data augmentation for fingerprint images.
Applies bounded geometric and photometric transforms that simulate real-world sensor variability
without disrupting core ridge flow or minutiae formations.
"""

import numpy as np
import cv2


class BiometricAugmentor:
    """
    Augmentation engine strictly preserving fingerprint biometric characteristics.
    """

    def __init__(
        self,
        rotation_range_deg: float = 12.0,
        shift_ratio: float = 0.06,
        scale_range: tuple = (0.95, 1.05),
        brightness_range: tuple = (0.9, 1.1),
        contrast_range: tuple = (0.9, 1.1),
        gaussian_noise_std: float = 0.02,
        seed: int = 42,
    ):
        self.rotation_range = rotation_range_deg
        self.shift_ratio = shift_ratio
        self.scale_range = scale_range
        self.brightness_range = brightness_range
        self.contrast_range = contrast_range
        self.noise_std = gaussian_noise_std
        self.rng = np.random.RandomState(seed)

    def __call__(self, img_normalized: np.ndarray) -> np.ndarray:
        """
        Takes normalized image of shape (H, W, 1) with values in [0, 1]
        and applies random biometric-preserving perturbations.
        """
        img = img_normalized.copy()
        h, w = img.shape[:2]

        # 1. Random small rotation & scaling
        angle = self.rng.uniform(-self.rotation_range, self.rotation_range)
        scale = self.rng.uniform(self.scale_range[0], self.scale_range[1])
        center = (w / 2.0, h / 2.0)
        M_rot = cv2.getRotationMatrix2D(center, angle, scale)

        # 2. Random translation
        dx = self.rng.uniform(-self.shift_ratio, self.shift_ratio) * w
        dy = self.rng.uniform(-self.shift_ratio, self.shift_ratio) * h
        M_rot[0, 2] += dx
        M_rot[1, 2] += dy

        # Apply affine transform with border replicate
        transformed = cv2.warpAffine(
            img[:, :, 0],
            M_rot,
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )

        # 3. Random Brightness and Contrast
        alpha = self.rng.uniform(self.contrast_range[0], self.contrast_range[1])
        beta = self.rng.uniform(self.brightness_range[0] - 1.0, self.brightness_range[1] - 1.0)
        transformed = alpha * transformed + beta

        # 4. Add subtle Gaussian noise to simulate sensor noise
        if self.noise_std > 0:
            noise = self.rng.normal(0.0, self.noise_std, size=(h, w))
            transformed += noise

        # Clip values to valid range [0, 1]
        transformed = np.clip(transformed, 0.0, 1.0).astype(np.float32)

        return np.expand_dims(transformed, axis=-1)

