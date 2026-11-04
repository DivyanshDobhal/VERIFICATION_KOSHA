"""
Model evaluation engine.
Executes test verification, measures latency, throughput, model footprint,
computes confidence intervals, and breakdowns across alteration categories and difficulties.
"""

from typing import Dict, Any, List, Tuple, Optional
import time
import os
from pathlib import Path
import numpy as np
import pandas as pd
import tensorflow as tf
from src.evaluation.metrics import (
    compute_classification_metrics,
    compute_biometric_verification_metrics,
    compute_identification_metrics,
)
from src.preprocessing.pipeline import FingerprintPreprocessor


def compute_95_ci(values: List[float]) -> Dict[str, float]:
    """Computes mean, standard deviation, and 95% confidence intervals."""
    arr = np.array(values, dtype=float)
    n = len(arr)
    mean = float(np.mean(arr))
    if n <= 1:
        return {"mean": mean, "std": 0.0, "ci_lower": mean, "ci_upper": mean}
    std = float(np.std(arr, ddof=1))
    margin = float(1.96 * (std / np.sqrt(n)))
    return {
        "mean": mean,
        "std": std,
        "ci_lower": float(mean - margin),
        "ci_upper": float(mean + margin),
    }


def evaluate_verification(
    model: tf.keras.Model,
    img1_paths: List[str],
    img2_paths: List[str],
    labels: np.ndarray,
    preprocessor: Optional[FingerprintPreprocessor] = None,
    threshold: Optional[float] = None,
    batch_size: int = 64,
) -> Dict[str, Any]:
    """
    Evaluates Siamese verification model on paired inputs.
    Measures latency, throughput, memory, verification curves, and classification metrics.
    """
    pre = preprocessor or FingerprintPreprocessor()

    # Preprocess images
    t0_prep = time.time()
    x1_list = [pre.process_image(p) for p in img1_paths]
    x2_list = [pre.process_image(p) for p in img2_paths]
    x1_arr = np.array(x1_list, dtype=np.float32)
    x2_arr = np.array(x2_list, dtype=np.float32)

    # Measure inference latency and throughput
    t0_infer = time.time()
    distances = model.predict([x1_arr, x2_arr], batch_size=batch_size, verbose=0).flatten()
    infer_time = time.time() - t0_infer

    num_pairs = len(labels)
    latency_ms_per_pair = float((infer_time / num_pairs) * 1000.0)
    throughput_pairs_sec = float(num_pairs / infer_time) if infer_time > 0 else 0.0

    # Biometric Verification Metrics
    verif_metrics = compute_biometric_verification_metrics(labels, distances)
    opt_threshold = threshold if threshold is not None else verif_metrics["eer_threshold_distance"]

    # Classification Metrics at optimal / specified threshold
    class_metrics = compute_classification_metrics(labels, distances, opt_threshold)

    # Model complexity metrics
    total_params = int(model.count_params())
    trainable_params = int(np.sum([tf.keras.backend.count_params(w) for w in model.trainable_weights]))

    eval_result = {
        "num_pairs_evaluated": num_pairs,
        "performance": {
            "inference_time_seconds": float(infer_time),
            "latency_ms_per_pair": latency_ms_per_pair,
            "throughput_pairs_per_sec": throughput_pairs_sec,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
        },
        "biometric_verification": verif_metrics,
        "classification": class_metrics,
        "predicted_distances": distances,
    }

    return eval_result

