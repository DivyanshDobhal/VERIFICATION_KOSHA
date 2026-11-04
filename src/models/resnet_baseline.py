"""
Comparison Model 2: ResNet50 Siamese Network for Fingerprint Recognition.
Adapts transfer learning with ResNet50 backbone for grayscale fingerprint embeddings.
"""

from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import ResNet50
from src.models.losses import EuclideanDistanceLayer


def build_resnet_feature_extractor(
    input_shape: Tuple[int, int, int] = (128, 128, 1),
    embedding_dim: int = 128,
) -> Model:
    """
    Constructs ResNet50-based feature extractor adapted for 128x128 grayscale input.
    """
    inputs = layers.Input(shape=input_shape, name="resnet_fingerprint_input")

    # Adapt single-channel grayscale to 3-channel for pretrained ResNet50
    x = layers.Conv2D(3, (1, 1), padding="same", name="channel_adapter")(inputs)

    # ResNet50 base without top
    base_resnet = ResNet50(
        include_top=False,
        weights=None,  # Trained from scratch or initialized for domain-specific fingerprints
        input_tensor=x,
    )

    x = layers.GlobalAveragePooling2D(name="resnet_gap")(base_resnet.output)
    x = layers.Dense(256, activation="relu", name="resnet_dense_256")(x)
    x = layers.Dropout(0.3, name="resnet_dropout")(x)
    x = layers.Dense(embedding_dim, name="resnet_dense_embedding")(x)
    embeddings = layers.Lambda(
        lambda t: tf.math.l2_normalize(t, axis=1), name="resnet_l2_norm"
    )(x)

    return Model(inputs=inputs, outputs=embeddings, name="resnet50_feature_extractor")


def build_resnet_siamese_network(
    input_shape: Tuple[int, int, int] = (128, 128, 1),
    embedding_dim: int = 128,
) -> Tuple[Model, Model]:
    """
    Constructs ResNet50 Siamese Network.
    """
    base_model = build_resnet_feature_extractor(input_shape, embedding_dim)

    input_a = layers.Input(shape=input_shape, name="resnet_branch_a")
    input_b = layers.Input(shape=input_shape, name="resnet_branch_b")

    emb_a = base_model(input_a)
    emb_b = base_model(input_b)

    distance = EuclideanDistanceLayer(name="resnet_euclidean_distance")([emb_a, emb_b])
    siamese_model = Model(
        inputs=[input_a, input_b], outputs=distance, name="resnet50_siamese_verifier"
    )

    return siamese_model, base_model

