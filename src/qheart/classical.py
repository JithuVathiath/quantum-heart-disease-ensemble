"""Leakage-safe classical benchmark and cross-cohort stress tests."""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.base import ClassifierMixin
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from qheart.config import ExperimentConfig
from qheart.data import CROSS_COHORT_FEATURES, FEATURES
from qheart.evaluation import classification_metrics
from qheart.preprocessing import quantum_preprocessor, tabular_preprocessor

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass
class OofResult:
    probabilities: dict[str, FloatArray]
    folds: list[dict[str, Any]]
    runtimes: dict[str, float]


def _model_factories(seed: int) -> dict[str, Callable[[], ClassifierMixin]]:
    return {
        "dummy_prior": lambda: DummyClassifier(strategy="prior"),
        "logistic_regression": lambda: LogisticRegression(
            C=1.0, class_weight="balanced", max_iter=2000, random_state=seed
        ),
        "rbf_svc": lambda: SVC(
            C=1.0,
            gamma="scale",
            probability=True,
            class_weight="balanced",
            random_state=seed,
        ),
        "rbf_svc_4d": lambda: SVC(
            C=1.0,
            gamma="scale",
            probability=True,
            class_weight="balanced",
            random_state=seed,
        ),
        "extra_trees": lambda: ExtraTreesClassifier(
            n_estimators=400,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=seed,
            n_jobs=-1,
        ),
        "hist_gradient_boosting": lambda: HistGradientBoostingClassifier(
            learning_rate=0.06,
            max_iter=250,
            max_leaf_nodes=15,
            l2_regularization=1.0,
            random_state=seed,
        ),
    }


def make_pipeline(model: ClassifierMixin, features: tuple[str, ...] = FEATURES) -> Pipeline:
    return Pipeline([("preprocess", tabular_preprocessor(features)), ("model", model)])


def benchmark_classical(
    frame: pd.DataFrame,
    config: ExperimentConfig,
    *,
    model_names: Iterable[str] | None = None,
) -> OofResult:
    factories = _model_factories(config.seed)
    selected = list(model_names) if model_names is not None else list(factories)
    unknown = sorted(set(selected) - set(factories))
    if unknown:
        raise ValueError(f"Unknown classical models: {unknown}")

    x = frame.loc[:, FEATURES]
    y = frame["target"].to_numpy(dtype=int)
    splitter = StratifiedKFold(n_splits=config.folds, shuffle=True, random_state=config.seed)
    splits = list(splitter.split(x, y))
    probabilities = {name: np.full(len(frame), np.nan, dtype=float) for name in selected}
    runtimes = {name: 0.0 for name in selected}
    fold_records: list[dict[str, Any]] = []

    for fold_index, (train_index, test_index) in enumerate(splits):
        for name in selected:
            pipeline = (
                Pipeline(
                    [
                        ("preprocess", quantum_preprocessor(config.quantum_features)),
                        ("model", factories[name]()),
                    ]
                )
                if name == "rbf_svc_4d"
                else make_pipeline(factories[name]())
            )
            started = time.perf_counter()
            pipeline.fit(x.iloc[train_index], y[train_index])
            score = pipeline.predict_proba(x.iloc[test_index])[:, 1]
            elapsed = time.perf_counter() - started
            probabilities[name][test_index] = score
            runtimes[name] += elapsed
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
        raise RuntimeError("Out-of-fold predictions are incomplete")
    return OofResult(probabilities=probabilities, folds=fold_records, runtimes=runtimes)


def cross_cohort_stress_test(
    cohorts: dict[str, pd.DataFrame], config: ExperimentConfig
) -> list[dict[str, Any]]:
    factories = _model_factories(config.seed)
    results: list[dict[str, Any]] = []
    for model_name in ("logistic_regression", "rbf_svc"):
        for source_name, source in cohorts.items():
            model = make_pipeline(factories[model_name](), CROSS_COHORT_FEATURES)
            started = time.perf_counter()
            model.fit(source.loc[:, CROSS_COHORT_FEATURES], source["target"].to_numpy(dtype=int))
            fit_seconds = time.perf_counter() - started
            for target_name, target in cohorts.items():
                probability = model.predict_proba(target.loc[:, CROSS_COHORT_FEATURES])[:, 1]
                y_target = target["target"].to_numpy(dtype=int)
                results.append(
                    {
                        "model": model_name,
                        "train_cohort": source_name,
                        "test_cohort": target_name,
                        "train_rows": len(source),
                        "test_rows": len(target),
                        "validation_type": (
                            "resubstitution" if source_name == target_name else "external"
                        ),
                        "roc_auc": round(float(roc_auc_score(y_target, probability)), 6),
                        "fit_seconds": round(fit_seconds, 6),
                    }
                )
    return results
