from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from qheart.data import COLUMNS


@pytest.fixture
def synthetic_frame() -> pd.DataFrame:
    generator = np.random.default_rng(42)
    rows = 100
    age = generator.integers(35, 78, rows)
    sex = generator.integers(0, 2, rows)
    oldpeak = np.maximum(generator.normal(1.0, 1.0, rows), 0)
    signal = -4.5 + 0.055 * age + 0.55 * sex + 0.45 * oldpeak
    probability = 1 / (1 + np.exp(-signal))
    target = generator.binomial(1, probability)
    frame = pd.DataFrame(
        {
            "age": age,
            "sex": sex,
            "cp": generator.integers(1, 5, rows),
            "trestbps": generator.normal(132, 16, rows),
            "chol": generator.normal(245, 45, rows),
            "fbs": generator.integers(0, 2, rows),
            "restecg": generator.integers(0, 3, rows),
            "thalach": generator.normal(150, 20, rows),
            "exang": generator.integers(0, 2, rows),
            "oldpeak": oldpeak,
            "slope": generator.integers(1, 4, rows),
            "ca": generator.integers(0, 4, rows),
            "thal": generator.choice([3, 6, 7], rows),
            "num": target,
            "target": target,
            "cohort": "synthetic",
            "row_id": [f"synthetic-{index:04d}" for index in range(rows)],
        }
    )
    frame.loc[[2, 9], "chol"] = np.nan
    return frame


@pytest.fixture
def cohort_writer(tmp_path: Path) -> Callable[[str, list[list[object]]], None]:
    root = tmp_path / "raw" / "uci-heart-disease"
    root.mkdir(parents=True)

    def write(filename: str, rows: list[list[object]]) -> None:
        assert all(len(row) == len(COLUMNS) for row in rows)
        (root / filename).write_text(
            "\n".join(",".join(str(value) for value in row) for row in rows) + "\n",
            encoding="utf-8",
        )

    return write
