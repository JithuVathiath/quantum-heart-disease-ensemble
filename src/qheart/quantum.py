"""Quantum-kernel evaluation and reproducible bootstrap aggregation."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC

from qheart.config import ExperimentConfig
from qheart.data import FEATURES
from qheart.evaluation import classification_metrics
from qheart.preprocessing import quantum_preprocessor

FloatArray = NDArray[np.float64]


class QuantumKernel(Protocol):
    def evaluate(
        self, x_vec: FloatArray, y_vec: FloatArray | None = None
    ) -> FloatArray: ...


@dataclass
class QuantumOofResult:
    probabilities: dict[str, FloatArray]
    folds: list[dict[str, Any]]
    diagnostics: list[dict[str, Any]]
    runtimes: dict[str, float]


def build_statevector_kernel(config: ExperimentConfig) -> QuantumKernel:
    """Create the official Qiskit statevector fidelity kernel lazily."""

    try:
        from qiskit.circuit.library import zz_feature_map
        from qiskit_machine_learning.kernels import FidelityStatevectorKernel
    except ImportError as exc:  # pragma: no cover - exercised in minimal installs
        raise RuntimeError(
            "Quantum dependencies are missing. Install with `pip install -e '.[quantum]'`."
        ) from exc

    feature_map = zz_feature_map(
        feature_dimension=config.quantum_features,
        reps=config.quantum_feature_map_reps,
        entanglement=config.quantum_entanglement,
    )
    return FidelityStatevectorKernel(
        feature_map=feature_map,
        auto_clear_cache=False,
        enforce_psd=True,
    )


def kernel_diagnostics(kernel: FloatArray, labels: NDArray[np.int64]) -> dict[str, float]:
    symmetric = (kernel + kernel.T) / 2.0
    eigenvalues = np.linalg.eigvalsh(symmetric)
    positive = np.clip(eigenvalues, 0.0, None)
    weights = positive / positive.sum() if positive.sum() else positive
    nonzero = weights[weights > 1e-15]
    effective_rank = float(np.exp(-np.sum(nonzero * np.log(nonzero)))) if nonzero.size else 0.0
    signed = np.where(labels == 1, 1.0, -1.0)
    target = np.outer(signed, signed)
    denominator = np.linalg.norm(symmetric) * np.linalg.norm(target)
    alignment = float(np.sum(symmetric * target) / denominator) if denominator else 0.0
    return {
        "kernel_target_alignment": alignment,
        "effective_rank": effective_rank,
        "largest_eigenvalue": float(eigenvalues[-1]),
        "smallest_eigenvalue": float(eigenvalues[0]),
        "condition_proxy": float(eigenvalues[-1] / max(positive[positive > 1e-12].min(), 1e-12))
        if np.any(positive > 1e-12)
        else 0.0,
    }


def _fit_precomputed_svc(
    train_kernel: FloatArray,
    labels: NDArray[np.int64],
    test_kernel: FloatArray,
    *,
    seed: int,
) -> FloatArray:
    model = SVC(
        kernel="precomputed",
        C=1.0,
        probability=True,
        class_weight="balanced",
        random_state=seed,
    )
    model.fit(train_kernel, labels)
    return np.asarray(model.predict_proba(test_kernel)[:, 1], dtype=float)


def bagged_kernel_svc_predict(
    train_kernel: FloatArray,
    labels: NDArray[np.int64],
    test_kernel: FloatArray,
    *,
    estimators: int,
    seed: int,
) -> FloatArray:
    """Bag precomputed quantum-kernel SVCs over deterministic bootstrap samples."""

    if estimators < 1:
        raise ValueError("estimators must be positive")
    generator = np.random.default_rng(seed)
    members: list[FloatArray] = []
    for member in range(estimators):
        for _ in range(100):
            indices = generator.integers(0, len(labels), len(labels))
            if np.unique(labels[indices]).size == 2:
                break
        else:  # pragma: no cover - only possible for pathological labels
            raise ValueError("Could not draw a two-class bootstrap sample")
        sampled_train = train_kernel[np.ix_(indices, indices)]
        sampled_test = test_kernel[:, indices]
        members.append(
            _fit_precomputed_svc(
                sampled_train,
                labels[indices],
                sampled_test,
                seed=seed + member + 1,
            )
        )
    return np.mean(np.vstack(members), axis=0)


def benchmark_quantum(frame: pd.DataFrame, config: ExperimentConfig) -> QuantumOofResult:
    x = frame.loc[:, FEATURES]
    y = frame["target"].to_numpy(dtype=int)
    splitter = StratifiedKFold(n_splits=config.folds, shuffle=True, random_state=config.seed)
    names = ("quantum_kernel_svc", "bagged_quantum_kernel_svc")
    probabilities = {name: np.full(len(frame), np.nan, dtype=float) for name in names}
    runtimes = {name: 0.0 for name in names}
    fold_records: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    kernel = build_statevector_kernel(config)

    for fold_index, (train_index, test_index) in enumerate(splitter.split(x, y)):
        transform = quantum_preprocessor(config.quantum_features)
        train_features = np.asarray(transform.fit_transform(x.iloc[train_index]), dtype=float)
        test_features = np.asarray(transform.transform(x.iloc[test_index]), dtype=float)

        kernel_started = time.perf_counter()
        train_kernel = np.asarray(kernel.evaluate(x_vec=train_features), dtype=float)
        test_kernel = np.asarray(
            kernel.evaluate(x_vec=test_features, y_vec=train_features), dtype=float
        )
        kernel_seconds = time.perf_counter() - kernel_started
        diagnostic = kernel_diagnostics(train_kernel, y[train_index])
        diagnostics.append(
            {
                "fold": fold_index,
                "qubits": config.quantum_features,
                "feature_map_reps": config.quantum_feature_map_reps,
                "kernel_seconds": round(kernel_seconds, 6),
                **{key: round(value, 6) for key, value in diagnostic.items()},
            }
        )

        started = time.perf_counter()
        single = _fit_precomputed_svc(
            train_kernel, y[train_index], test_kernel, seed=config.seed + fold_index
        )
        single_seconds = time.perf_counter() - started + kernel_seconds
        probabilities["quantum_kernel_svc"][test_index] = single
        runtimes["quantum_kernel_svc"] += single_seconds

        started = time.perf_counter()
        bagged = bagged_kernel_svc_predict(
            train_kernel,
            y[train_index],
            test_kernel,
            estimators=config.bagging_estimators,
            seed=config.seed + fold_index * 100,
        )
        bagged_seconds = time.perf_counter() - started + kernel_seconds
        probabilities["bagged_quantum_kernel_svc"][test_index] = bagged
        runtimes["bagged_quantum_kernel_svc"] += bagged_seconds

        for name, score, elapsed in (
            ("quantum_kernel_svc", single, single_seconds),
            ("bagged_quantum_kernel_svc", bagged, bagged_seconds),
        ):
            fold_records.append(
                {
                    "fold": fold_index,
                    "model": name,
                    "train_rows": len(train_index),
                    "test_rows": len(test_index),
                    "runtime_seconds": round(elapsed, 6),
                    **{
                        key: round(value, 6)
                        for key, value in classification_metrics(y[test_index], score).items()
                        if isinstance(value, float)
                    },
                }
            )

    if any(np.isnan(scores).any() for scores in probabilities.values()):
        raise RuntimeError("Quantum out-of-fold predictions are incomplete")
    return QuantumOofResult(probabilities, fold_records, diagnostics, runtimes)

