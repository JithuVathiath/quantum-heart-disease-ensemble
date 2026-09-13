"""Fold-local transformations for full and compute-matched model tracks."""

from __future__ import annotations

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler

from qheart.data import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES


def tabular_preprocessor(features: tuple[str, ...] = FEATURES) -> ColumnTransformer:
    numeric = [name for name in NUMERIC_FEATURES if name in features]
    categorical = [name for name in CATEGORICAL_FEATURES if name in features]
    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        (
                            "imputer",
                            SimpleImputer(strategy="most_frequent", keep_empty_features=True),
                        ),
                        (
                            "encode",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                categorical,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def quantum_preprocessor(feature_count: int) -> Pipeline:
    return Pipeline(
        [
            ("tabular", tabular_preprocessor()),
            ("pca", PCA(n_components=feature_count, random_state=0)),
            ("angles", MinMaxScaler(feature_range=(0.0, float(np.pi)))),
        ]
    )

