"""Metrics and uncertainty utilities shared across benchmark tracks."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


def expected_calibration_error(
    y_true: IntArray, probability: FloatArray, *, bins: int = 10
) -> float:
    if bins < 2:
        raise ValueError("bins must be at least 2")
    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.minimum(np.digitize(probability, edges[1:-1]), bins - 1)
    error = 0.0
    for index in range(bins):
        mask = assignments == index
        if not np.any(mask):
            continue
        error += float(mask.mean()) * abs(float(probability[mask].mean() - y_true[mask].mean()))
    return float(error)


def classification_metrics(y_true: IntArray, probability: FloatArray) -> dict[str, float]:
    prediction = (probability >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    return {
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "accuracy": float(accuracy_score(y_true, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, prediction)),
        "precision": float(precision_score(y_true, prediction, zero_division=0)),
        "sensitivity": float(recall_score(y_true, prediction, zero_division=0)),
        "specificity": float(specificity),
        "f1": float(f1_score(y_true, prediction, zero_division=0)),
        "brier": float(brier_score_loss(y_true, probability)),
        "ece": expected_calibration_error(y_true, probability),
        "true_negative": float(tn),
        "false_positive": float(fp),
        "false_negative": float(fn),
        "true_positive": float(tp),
    }


def bootstrap_interval(
    y_true: IntArray,
    probability: FloatArray,
    metric: Callable[[IntArray, FloatArray], float],
    *,
    samples: int,
    seed: int,
    confidence: float = 0.95,
) -> dict[str, float]:
    if samples < 100:
        raise ValueError("samples must be at least 100")
    generator = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(samples):
        indices = generator.integers(0, len(y_true), len(y_true))
        sampled_y = y_true[indices]
        if np.unique(sampled_y).size < 2:
            continue
        values.append(metric(sampled_y, probability[indices]))
    if not values:
        raise ValueError("No valid bootstrap samples")
    alpha = (1.0 - confidence) / 2.0
    return {
        "estimate": float(metric(y_true, probability)),
        "lower": float(np.quantile(values, alpha)),
        "upper": float(np.quantile(values, 1.0 - alpha)),
    }


def paired_bootstrap_difference(
    y_true: IntArray,
    first: FloatArray,
    second: FloatArray,
    *,
    samples: int,
    seed: int,
) -> dict[str, float | str]:
    generator = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(samples):
        indices = generator.integers(0, len(y_true), len(y_true))
        sampled_y = y_true[indices]
        if np.unique(sampled_y).size < 2:
            continue
        values.append(
            float(roc_auc_score(sampled_y, first[indices]))
            - float(roc_auc_score(sampled_y, second[indices]))
        )
    estimate = float(roc_auc_score(y_true, first) - roc_auc_score(y_true, second))
    return {
        "metric": "roc_auc_difference",
        "estimate": estimate,
        "lower": float(np.quantile(values, 0.025)),
        "upper": float(np.quantile(values, 0.975)),
        "probability_first_better": float(np.mean(np.asarray(values) > 0)),
    }


def metric_with_interval(
    y_true: IntArray,
    probability: FloatArray,
    *,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    metrics: dict[str, Any] = classification_metrics(y_true, probability)
    roc_interval = bootstrap_interval(
        y_true,
        probability,
        lambda truth, score: float(roc_auc_score(truth, score)),
        samples=samples,
        seed=seed,
    )
    balanced_interval = bootstrap_interval(
        y_true,
        probability,
        lambda truth, score: float(
            balanced_accuracy_score(truth, (score >= 0.5).astype(int))
        ),
        samples=samples,
        seed=seed + 1,
    )
    metrics["roc_auc_interval"] = roc_interval
    metrics["balanced_accuracy_interval"] = balanced_interval
    return metrics
