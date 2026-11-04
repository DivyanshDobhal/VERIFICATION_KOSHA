"""
Configuration settings for KOSHA LABS Biometric Fingerprint Recognition System.
"""
import os
# Ensure TensorFlow runtime initializes before pyarrow / pandas
import tensorflow as tf
from pathlib import Path

# Stabilize OpenMP thread pools on macOS
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["TF_NUM_INTRAOP_THREADS"] = "2"
os.environ["TF_NUM_INTEROP_THREADS"] = "2"

# Base paths
PROJECT_ROOT = Path("/Users/divyanshdobhal/Desktop/PROJECTS/KOSHA_VERIFICATION")
DATASET_ROOT = Path("/Users/divyanshdobhal/Downloads/SOCOFing")
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
REPORTS_DIR = RESULTS_DIR / "reports"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
GALLERY_STORE_DIR = PROJECT_ROOT / "gallery_store"

# Ensure runtime directories exist
for p in [RESULTS_DIR, PLOTS_DIR, REPORTS_DIR, CHECKPOINTS_DIR, GALLERY_STORE_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Dataset subdirectories
REAL_DIR = DATASET_ROOT / "Real"
ALTERED_DIR = DATASET_ROOT / "Altered"
ALTERED_EASY_DIR = ALTERED_DIR / "Altered-Easy"
ALTERED_MEDIUM_DIR = ALTERED_DIR / "Altered-Medium"
ALTERED_HARD_DIR = ALTERED_DIR / "Altered-Hard"

# Image processing configuration
IMG_HEIGHT = 128
IMG_WIDTH = 128
IMG_CHANNELS = 1
IMG_SHAPE = (IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS)

CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# Augmentation parameters
AUGMENTATION_CONFIG = {
    "rotation_range_deg": 12.0,
    "width_shift_range": 0.06,
    "height_shift_range": 0.06,
    "zoom_range": 0.05,
    "brightness_range": (0.9, 1.1),
    "gaussian_noise_std": 0.02,
}

# Model architecture & training hyperparameters
EMBEDDING_DIM = 128
CONTRASTIVE_MARGIN = 1.0
LEARNING_RATE = 1e-4
BATCH_SIZE = 32
DEFAULT_EPOCHS = 50
CV_FOLDS = 5
RANDOM_SEED = 42

# Operational Biometric Verification Thresholds (Euclidean distance on L2-normalized embeddings)
# Embeddings lie on unit hypersphere; dist in [0, 2].
# Matching identity: distance < THRESHOLD
DEFAULT_EER_THRESHOLD = 0.85
STRICT_FAR_01_THRESHOLD = 0.65  # Target FAR <= 0.1% for high security
STANDARD_FAR_1_THRESHOLD = 0.75 # Target FAR <= 1.0%

# Identification Top-K
TOP_K_IDENTIFICATION = 5
