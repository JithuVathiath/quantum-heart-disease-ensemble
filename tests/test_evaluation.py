from __future__ import annotations

import numpy as np
import pytest

from qheart.evaluation import (
    bootstrap_interval,
    classification_metrics,
    expected_calibration_error,
    metric_with_interval,
    paired_bootstrap_difference,
)


def test_perfect_probabilities_have_expected_metrics() -> None:
    truth = np.array([0, 0, 1, 1], dtype=int)
    score = np.array([0.05, 0.1, 0.9, 0.95], dtype=float)
    metrics = classification_metrics(truth, score)
    assert metrics["roc_auc"] == 1.0
    assert metrics["balanced_accuracy"] == 1.0
    assert metrics["false_negative"] == 0
    assert metrics["brier"] < 0.02


def test_calibration_error_validates_bins() -> None:
    with pytest.raises(ValueError, match="bins"):
        expected_calibration_error(np.array([0, 1]), np.array([0.2, 0.8]), bins=1)


def test_bootstrap_outputs_are_deterministic() -> None:
    truth = np.array([0, 1] * 30, dtype=int)
    score = np.linspace(0.01, 0.99, 60)

    def metric(y, p) -> float:
        return float(np.mean((p >= 0.5) == y))

    first = bootstrap_interval(truth, score, metric, samples=100, seed=7)
    second = bootstrap_interval(truth, score, metric, samples=100, seed=7)
    assert first == second
    assert first["lower"] <= first["estimate"] <= first["upper"]


def test_intervals_and_paired_difference_have_required_fields() -> None:
    truth = np.array([0, 1] * 40, dtype=int)
    first = np.where(truth == 1, 0.8, 0.2).astype(float)
    second = np.linspace(0.1, 0.9, len(truth))
    evidence = metric_with_interval(truth, first, samples=100, seed=4)
    difference = paired_bootstrap_difference(
        truth, first, second, samples=100, seed=4
    )
    assert "roc_auc_interval" in evidence
    assert difference["probability_first_better"] > 0.9
