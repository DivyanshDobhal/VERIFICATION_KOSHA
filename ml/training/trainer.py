"""
Siamese Model Trainer.
Manages compilation, callbacks (ReduceLROnPlateau, EarlyStopping, ModelCheckpoint),
and training execution for Siamese networks.
"""

from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import time
import tensorflow as tf
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint,
    TensorBoard,
)
from ml.models.losses import contrastive_loss
from ml.data.pair_generator import SiameseBatchGenerator


class SiameseTrainer:
    """
    Standardized trainer for Siamese architectures.
    """

    def __init__(
        self,
        siamese_model: tf.keras.Model,
        feature_extractor: tf.keras.Model,
        learning_rate: float = 1e-4,
        margin: float = 1.0,
        checkpoint_dir: Optional[Path] = None,
    ):
        self.siamese_model = siamese_model
        self.feature_extractor = feature_extractor
        self.learning_rate = learning_rate
        self.margin = margin
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else Path("./checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Compile model with Contrastive Loss
        optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        self.siamese_model.compile(
            optimizer=optimizer,
            loss=contrastive_loss(margin=margin),
        )

    def train(
        self,
        train_data: Any,
        val_data: Any,
        epochs: int = 50,
        batch_size: int = 32,
        fold_id: Optional[int] = None,
    ) -> Tuple[Dict[str, Any], Path]:
        """
        Executes Siamese training with callbacks.
        train_data can be:
        - tuple: ((x1, x2), y)
        - generator/sequence
        """
        prefix = f"fold_{fold_id}_" if fold_id is not None else ""
        ckpt_path = self.checkpoint_dir / f"{prefix}best_siamese_model.weights.h5"

        callbacks = [
            EarlyStopping(
                monitor="val_loss",
                patience=6,
                restore_best_weights=True,
                verbose=0,
            ),
            ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=3,
                min_lr=1e-6,
                verbose=0,
            ),
            ModelCheckpoint(
                filepath=str(ckpt_path),
                monitor="val_loss",
                save_best_only=True,
                save_weights_only=True,
                verbose=0,
            ),
        ]

        t0 = time.time()
        if isinstance(train_data, tuple) and len(train_data) == 2:
            x_train, y_train = train_data
            x_val, y_val = val_data
            history = self.siamese_model.fit(
                list(x_train),
                y_train,
                validation_data=(list(x_val), y_val),
                batch_size=batch_size,
                epochs=epochs,
                callbacks=callbacks,
                verbose=2,
            )
        else:
            history = self.siamese_model.fit(
                train_data,
                validation_data=val_data,
                epochs=epochs,
                callbacks=callbacks,
                verbose=2,
            )
        train_time = time.time() - t0

        # Extract history
        hist_dict = {k: [float(val) for val in v] for k, v in history.history.items()}
        hist_dict["training_time_seconds"] = train_time
        hist_dict["best_epoch"] = int(np.argmin(hist_dict["val_loss"]) + 1)
        hist_dict["best_val_loss"] = float(np.min(hist_dict["val_loss"]))

        return hist_dict, ckpt_path


import numpy as np
