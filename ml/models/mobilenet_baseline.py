"""
Comparison Model 3: MobileNetV3 Siamese Network for Mobile Edge Fingerprint Recognition.
"""

from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV3Small
from ml.models.losses import EuclideanDistanceLayer


def build_mobilenet_feature_extractor(
    input_shape: Tuple[int, int, int] = (128, 128, 1),
    embedding_dim: int = 128,
) -> Model:
    """
    Constructs MobileNetV3Small feature extractor adapted for 128x128 grayscale input.
    """
    inputs = layers.Input(shape=input_shape, name="mobilenet_fingerprint_input")

    # Adapt single-channel to 3-channel
    x = layers.Conv2D(3, (1, 1), padding="same", name="mobilenet_channel_adapter")(inputs)

    base_mobilenet = MobileNetV3Small(
        include_top=False,
        weights=None,
        input_tensor=x,
        pooling="avg",
    )

    x = layers.Dense(128, activation="relu", name="mobilenet_dense_128")(base_mobilenet.output)
    x = layers.Dropout(0.2, name="mobilenet_dropout")(x)
    x = layers.Dense(embedding_dim, name="mobilenet_dense_embedding")(x)
    embeddings = layers.Lambda(
        lambda t: tf.math.l2_normalize(t, axis=1), name="mobilenet_l2_norm"
    )(x)

    return Model(inputs=inputs, outputs=embeddings, name="mobilenetv3_feature_extractor")


def build_mobilenet_siamese_network(
    input_shape: Tuple[int, int, int] = (128, 128, 1),
    embedding_dim: int = 128,
) -> Tuple[Model, Model]:
    """
    Constructs MobileNetV3 Siamese Network.
    """
    base_model = build_mobilenet_feature_extractor(input_shape, embedding_dim)

    input_a = layers.Input(shape=input_shape, name="mobilenet_branch_a")
    input_b = layers.Input(shape=input_shape, name="mobilenet_branch_b")

    emb_a = base_model(input_a)
    emb_b = base_model(input_b)

    distance = EuclideanDistanceLayer(name="mobilenet_euclidean_distance")([emb_a, emb_b])
    siamese_model = Model(
        inputs=[input_a, input_b], outputs=distance, name="mobilenetv3_siamese_verifier"
    )

    return siamese_model, base_model

