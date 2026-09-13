"""Aggregate benchmark evidence without publishing patient-level records."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from qheart.config import ExperimentConfig
from qheart.evaluation import classification_metrics, metric_with_interval

FloatArray = NDArray[np.float64]


def build_leaderboard(
    y_true: NDArray[np.int64],
    probabilities: dict[str, FloatArray],
    runtimes: dict[str, float],
    config: ExperimentConfig,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset, (name, score) in enumerate(probabilities.items()):
        evidence = metric_with_interval(
            y_true,
            score,
            samples=config.bootstrap_samples,
            seed=config.seed + offset * 10,
        )
        rows.append(
            {
                "model": name,
                "track": "quantum" if "quantum" in name else "classical",
                "runtime_seconds": round(runtimes[name], 6),
                **_round_nested(evidence),
            }
        )
    return sorted(rows, key=lambda item: item["roc_auc"], reverse=True)


def subgroup_analysis(
    frame: pd.DataFrame,
    probabilities: dict[str, FloatArray],
    *,
    minimum_size: int,
) -> list[dict[str, Any]]:
    definitions = {
        "sex_female": frame["sex"].to_numpy() == 0,
        "sex_male": frame["sex"].to_numpy() == 1,
        "age_under_60": frame["age"].to_numpy() < 60,
        "age_60_or_over": frame["age"].to_numpy() >= 60,
    }
    y = frame["target"].to_numpy(dtype=int)
    rows: list[dict[str, Any]] = []
    for model, score in probabilities.items():
        for group, mask in definitions.items():
            count = int(mask.sum())
            positives = int(y[mask].sum())
            if count < minimum_size or np.unique(y[mask]).size < 2:
                rows.append(
                    {
                        "model": model,
                        "group": group,
                        "rows": count,
                        "positive_rows": positives,
                        "status": "suppressed",
                    }
                )
                continue
            metrics = classification_metrics(y[mask], score[mask])
            rows.append(
                {
                    "model": model,
                    "group": group,
                    "rows": count,
                    "positive_rows": positives,
                    "status": "reported",
                    **{key: round(value, 6) for key, value in metrics.items()},
                }
            )
    return rows


def calibration_bins(
    y_true: NDArray[np.int64], probability: FloatArray, *, bins: int = 10
) -> list[dict[str, Any]]:
    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.minimum(np.digitize(probability, edges[1:-1]), bins - 1)
    rows: list[dict[str, Any]] = []
    for index in range(bins):
        mask = assignments == index
        if not np.any(mask):
            continue
        rows.append(
            {
                "bin": index,
                "rows": int(mask.sum()),
                "mean_probability": round(float(probability[mask].mean()), 6),
                "observed_rate": round(float(y_true[mask].mean()), 6),
            }
        )
    return rows


def _round_nested(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, dict):
        return {key: _round_nested(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_round_nested(item) for item in value]
    return value
