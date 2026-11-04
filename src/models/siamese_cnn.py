"""
Primary Model: Siamese CNN with Shared Weights for Biometric Fingerprint Recognition.
Implements the 4-block convolutional feature extractor, L2-normalized 128-D embedding space,
and Euclidean distance layer.
"""

from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers, Model
from src.models.losses import EuclideanDistanceLayer


def build_base_cnn(
    input_shape: Tuple[int, int, int] = (128, 128, 1),
    embedding_dim: int = 128,
    dropout_rate: float = 0.3,
) -> Model:
    """
    Constructs the shared feature extractor branch:
    Block 1: Conv2D(32) -> BatchNorm -> ReLU -> MaxPool
    Block 2: Conv2D(64) -> BatchNorm -> ReLU -> MaxPool
    Block 3: Conv2D(128) -> BatchNorm -> ReLU -> MaxPool
    Block 4: Conv2D(256) -> BatchNorm -> ReLU
    Feature Extraction: GlobalAveragePooling2D -> Dense(256, ReLU) -> Dropout -> Dense(128) -> L2 Normalization
    """
    inputs = layers.Input(shape=input_shape, name="fingerprint_input")

    # Block 1
    x = layers.Conv2D(32, (3, 3), padding="same", name="conv1")(inputs)
    x = layers.BatchNormalization(name="bn1")(x)
    x = layers.ReLU(name="relu1")(x)
    x = layers.MaxPooling2D((2, 2), name="pool1")(x)

    # Block 2
    x = layers.Conv2D(64, (3, 3), padding="same", name="conv2")(x)
    x = layers.BatchNormalization(name="bn2")(x)
    x = layers.ReLU(name="relu2")(x)
    x = layers.MaxPooling2D((2, 2), name="pool2")(x)

    # Block 3
    x = layers.Conv2D(128, (3, 3), padding="same", name="conv3")(x)
    x = layers.BatchNormalization(name="bn3")(x)
    x = layers.ReLU(name="relu3")(x)
    x = layers.MaxPooling2D((2, 2), name="pool3")(x)

    # Block 4
    x = layers.Conv2D(256, (3, 3), padding="same", name="conv4")(x)
    x = layers.BatchNormalization(name="bn4")(x)
    x = layers.ReLU(name="relu4")(x)

    # Feature extraction & Embedding Projection
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.Dense(256, activation="relu", name="dense_proj")(x)
    x = layers.Dropout(dropout_rate, name="dropout")(x)
    x = layers.Dense(embedding_dim, name="embedding_dense")(x)

    # L2 normalization enforces unit hypersphere representation
    embeddings = layers.Lambda(
        lambda t: tf.math.l2_normalize(t, axis=1), name="l2_norm"
    )(x)

    return Model(inputs=inputs, outputs=embeddings, name="fingerprint_feature_extractor")


def build_siamese_network(
    input_shape: Tuple[int, int, int] = (128, 128, 1),
    embedding_dim: int = 128,
    dropout_rate: float = 0.3,
) -> Tuple[Model, Model]:
    """
    Assembles the complete Siamese Network with shared weights.
    Returns:
        siamese_model: Dual input model outputting Euclidean distance
        feature_extractor: Shared single-input submodel for generating 128-D embeddings directly
    """
    base_model = build_base_cnn(
        input_shape=input_shape,
        embedding_dim=embedding_dim,
        dropout_rate=dropout_rate,
    )

    input_a = layers.Input(shape=input_shape, name="image_branch_a")
    input_b = layers.Input(shape=input_shape, name="image_branch_b")

    # Shared weight embeddings
    embedding_a = base_model(input_a)
    embedding_b = base_model(input_b)

    # Distance layer
    distance = EuclideanDistanceLayer(name="euclidean_distance")([embedding_a, embedding_b])

    siamese_model = Model(
        inputs=[input_a, input_b],
        outputs=distance,
        name="siamese_fingerprint_verifier",
    )

    return siamese_model, base_model

