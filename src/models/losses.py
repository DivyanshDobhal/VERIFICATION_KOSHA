"""
Loss functions and distance layers for Siamese Fingerprint Recognition.
Implements Contrastive Loss with configurable margin and Euclidean Distance Layer.
"""

import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Layer


class EuclideanDistanceLayer(Layer):
    """
    Computes pairwise Euclidean distance between two embedding vectors:
    d = sqrt(sum((e1 - e2)^2) + eps)
    """

    def __init__(self, **kwargs):
        super(EuclideanDistanceLayer, self).__init__(**kwargs)

    def call(self, inputs):
        emb1, emb2 = inputs
        sum_sq = K.sum(K.square(emb1 - emb2), axis=1, keepdims=True)
        return K.sqrt(K.maximum(sum_sq, K.epsilon()))

    def get_config(self):
        return super(EuclideanDistanceLayer, self).get_config()


def contrastive_loss(margin: float = 1.0):
    """
    Contrastive loss for biometric verification.
    y_true: 1 for Genuine (same identity), 0 for Imposter (different identity)
    y_pred: Euclidean distance between embeddings

    L = y_true * d^2 + (1 - y_true) * max(0, margin - d)^2
    """

    def loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        # Genuine loss: penalize larger distances between genuine pairs
        genuine_loss = y_true * K.square(y_pred)
        # Imposter loss: penalize imposter distances less than margin
        imposter_loss = (1.0 - y_true) * K.square(K.maximum(margin - y_pred, 0.0))
        return K.mean(genuine_loss + imposter_loss)

    return loss

