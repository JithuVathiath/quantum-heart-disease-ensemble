from __future__ import annotations

import json

from qheart.benchmark import generate_public_outputs
from qheart.config import ExperimentConfig
from qheart.data import COHORT_FILES


def make_rows(count: int) -> list[list[object]]:
    rows: list[list[object]] = []
    for index in range(count):
        target = index % 2
        rows.append(
            [
                40 + index % 30,
                index % 2,
                1 + index % 4,
                110 + index % 35,
                190 + index * 2,
                index % 2,
                index % 3,
                175 - index % 45,
                target,
                float(index % 6) / 2,
                1 + index % 3,
                index % 4,
                [3, 6, 7][index % 3],
                target,
            ]
        )
    return rows


def test_classical_end_to_end_generates_public_outputs(tmp_path, cohort_writer) -> None:
    for filename in COHORT_FILES.values():
        cohort_writer(filename, make_rows(40))
    config = ExperimentConfig(
        experiment_id="integration-test",
        folds=2,
        bootstrap_samples=100,
        bagging_estimators=1,
        minimum_subgroup_size=10,
    )
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config.to_dict()), encoding="utf-8")
    results = tmp_path / "results.json"
    report = tmp_path / "results.md"
    payload = generate_public_outputs(
        tmp_path,
        config_path,
        results,
        report,
        include_quantum=False,
    )
    assert results.exists()
    assert report.exists()
    assert len(payload["leaderboard"]) == 6
    assert len(payload["transportability"]) == 32
    assert payload["primary_comparison"] is None
    assert "historical_publication_result" in json.dumps(payload)
