from __future__ import annotations

import numpy as np

from qheart.config import ExperimentConfig
from qheart.quantum import build_statevector_kernel


def test_official_qiskit_kernel_is_symmetric_and_bounded() -> None:
    config = ExperimentConfig(
        folds=2,
        bootstrap_samples=100,
        quantum_features=2,
        quantum_feature_map_reps=1,
        bagging_estimators=1,
    )
    kernel = build_statevector_kernel(config)
    points = np.array([[0.1, 0.2], [0.5, 0.7], [1.0, 0.4]])
    matrix = np.asarray(kernel.evaluate(x_vec=points))
    assert matrix.shape == (3, 3)
    assert np.allclose(matrix, matrix.T)
    assert np.allclose(np.diag(matrix), 1.0)
    assert np.all((matrix >= -1e-9) & (matrix <= 1 + 1e-9))
