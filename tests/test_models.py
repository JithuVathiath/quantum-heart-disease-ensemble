from __future__ import annotations

import numpy as np

from qheart.classical import benchmark_classical
from qheart.config import ExperimentConfig
from qheart.preprocessing import quantum_preprocessor, tabular_preprocessor
from qheart.quantum import bagged_kernel_svc_predict, benchmark_quantum, kernel_diagnostics


def small_config() -> ExperimentConfig:
    return ExperimentConfig(
        folds=3,
        bootstrap_samples=100,
        quantum_features=3,
        bagging_estimators=3,
        minimum_subgroup_size=10,
    )


def test_preprocessors_are_fold_fit_and_finite(synthetic_frame) -> None:
    full = tabular_preprocessor().fit_transform(synthetic_frame)
    quantum = quantum_preprocessor(3).fit_transform(synthetic_frame)
    assert full.shape[0] == len(synthetic_frame)
    assert quantum.shape == (len(synthetic_frame), 3)
    assert np.isfinite(full).all()
    assert np.isfinite(quantum).all()
    assert quantum.min() >= 0
    assert quantum.max() <= np.pi + 1e-9


def test_classical_oof_benchmark_is_complete(synthetic_frame) -> None:
    result = benchmark_classical(
        synthetic_frame,
        small_config(),
        model_names=["dummy_prior", "logistic_regression"],
    )
    assert set(result.probabilities) == {"dummy_prior", "logistic_regression"}
    assert len(result.folds) == 6
    assert all(np.isfinite(score).all() for score in result.probabilities.values())


def test_bagged_kernel_predictions_are_deterministic() -> None:
    points = np.array([[0.0], [0.2], [0.8], [1.0], [0.1], [0.9]])
    labels = np.array([0, 0, 1, 1, 0, 1])
    train_kernel = np.exp(-((points - points.T) ** 2))
    first = bagged_kernel_svc_predict(
        train_kernel, labels, train_kernel, estimators=3, seed=22
    )
    second = bagged_kernel_svc_predict(
        train_kernel, labels, train_kernel, estimators=3, seed=22
    )
    assert np.allclose(first, second)
    assert np.all((first >= 0) & (first <= 1))


def test_kernel_diagnostics_are_finite() -> None:
    kernel = np.array([[1.0, 0.2, 0.1], [0.2, 1.0, 0.3], [0.1, 0.3, 1.0]])
    values = kernel_diagnostics(kernel, np.array([0, 0, 1]))
    assert values["effective_rank"] > 1
    assert all(np.isfinite(value) for value in values.values())


def test_quantum_oof_benchmark_is_complete(synthetic_frame) -> None:
    config = ExperimentConfig(
        folds=2,
        bootstrap_samples=100,
        quantum_features=2,
        quantum_feature_map_reps=1,
        bagging_estimators=1,
        minimum_subgroup_size=10,
    )
    result = benchmark_quantum(synthetic_frame.iloc[:40].copy(), config)
    assert len(result.diagnostics) == 2
    assert len(result.folds) == 4
    assert all(np.isfinite(score).all() for score in result.probabilities.values())

