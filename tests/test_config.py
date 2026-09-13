from __future__ import annotations

import json

import pytest

from qheart.config import ExperimentConfig


def test_configuration_round_trip_and_fingerprint(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(ExperimentConfig().to_dict()), encoding="utf-8")
    first = ExperimentConfig.from_json(path)
    second = ExperimentConfig.from_json(path)
    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 16


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"folds": 1}, "folds"),
        ({"bootstrap_samples": 99}, "bootstrap"),
        ({"quantum_features": 1}, "quantum_features"),
        ({"bagging_estimators": 0}, "bagging"),
        ({"quantum_entanglement": "random"}, "entanglement"),
    ],
)
def test_invalid_configuration_is_rejected(kwargs, message) -> None:
    with pytest.raises(ValueError, match=message):
        ExperimentConfig(**kwargs)
