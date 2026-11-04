import os
import glob
from typing import Optional, Any, Dict
import numpy as np

DEFAULT_LOCAL_PATH = "/Users/divyanshdobhal/Desktop/PROJECTS/KOSHA_VERIFICATION"
FALLBACK_WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")

class SiameseModelManager:
    """Manages TensorFlow/Keras Siamese CNN model lifecycle.
    Auto-discovers existing trained model from /Users/divyanshdobhal/Desktop/PROJECTS/KOSHA_VERIFICATION
    or MODEL_PATH/KOSHA_MODEL_DIR environment variables.
    Enforces strict requirement: Never retrain or redesign the existing model.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv("MODEL_PATH") or os.getenv("KOSHA_MODEL_DIR") or DEFAULT_LOCAL_PATH
        self.model: Optional[Any] = None
        self.is_loaded: bool = False
        self.version: str = "kosha-siamese-v1.4"
        self.embedding_dimension: int = 128
        self.input_shape: tuple = (128, 128, 1)
        self.resolved_model_file: Optional[str] = None
        self.model_summary_info: Dict[str, Any] = {}
        self._try_load_model()

    def _discover_model_file(self, base_path: str) -> Optional[str]:
        """Scans directory for .keras, .h5, or SavedModel folders."""
        if not os.path.exists(base_path):
            return None
        
        # If directly pointing to a file
        if os.path.isfile(base_path):
            return base_path

        # If directory contains saved_model.pb
        if os.path.isdir(base_path):
            if os.path.exists(os.path.join(base_path, "saved_model.pb")):
                return base_path
            
            # Look for .keras, .h5 files
            patterns = ["*.keras", "*.h5", "**/*.keras", "**/*.h5"]
            for pat in patterns:
                matches = glob.glob(os.path.join(base_path, pat), recursive=True)
                if matches:
                    return matches[0]

        return None

    def _try_load_model(self):
        # 1. Search in user's KOSHA_VERIFICATION path or custom path
        candidate_paths = [
            self.model_path,
            DEFAULT_LOCAL_PATH,
            FALLBACK_WEIGHTS_DIR,
            os.path.join(os.getcwd(), "backend", "app", "ml", "weights"),
            os.path.join(os.getcwd(), "weights")
        ]

        found_path = None
        for p in candidate_paths:
            found = self._discover_model_file(p)
            if found:
                found_path = found
                break

        if not found_path:
            self.model = None
            self.is_loaded = False
            self.resolved_model_file = None
            return

        try:
            import tensorflow as tf
            self.resolved_model_file = found_path
            self.model = tf.keras.models.load_model(found_path, compile=False)
            self.is_loaded = True
            
            # Inspect input/output shapes
            try:
                if hasattr(self.model, "input_shape") and self.model.input_shape:
                    self.input_shape = self.model.input_shape
                if hasattr(self.model, "output_shape") and self.model.output_shape:
                    out_dim = self.model.output_shape[-1]
                    if isinstance(out_dim, int):
                        self.embedding_dimension = out_dim
            except Exception:
                pass

            self.model_summary_info = {
                "file": self.resolved_model_file,
                "input_shape": str(self.input_shape),
                "embedding_dimension": self.embedding_dimension,
                "framework": "TensorFlow/Keras",
                "normalization": "Unit L2 normalized",
            }
        except Exception as e:
            self.model = None
            self.is_loaded = False
            self.model_summary_info = {"error": str(e), "attempted_path": found_path}

    def is_configured(self) -> bool:
        return self.is_loaded and self.model is not None

    def extract_128d_embedding(self, preprocessed_tensor: np.ndarray) -> np.ndarray:
        if not self.is_configured():
            raise RuntimeError("MODEL_NOT_CONFIGURED")
        # Add batch dimension if needed
        if preprocessed_tensor.ndim == 3:
            batch_input = np.expand_dims(preprocessed_tensor, axis=0)
        else:
            batch_input = preprocessed_tensor

        raw_pred = self.model.predict(batch_input, verbose=0)
        if isinstance(raw_pred, list):
            raw_pred = raw_pred[0]

        embedding = np.array(raw_pred, dtype=np.float32).flatten()
        # L2 unit normalization
        norm = np.linalg.norm(embedding)
        if norm > 1e-12:
            embedding = embedding / norm
        return embedding

model_manager = SiameseModelManager()
