from __future__ import annotations

import json

import numpy as np

from qheart.analysis import build_leaderboard, calibration_bins, subgroup_analysis
from qheart.config import ExperimentConfig
from qheart.reporting import canonical_hash, write_markdown_report, write_results


def config() -> ExperimentConfig:
    return ExperimentConfig(folds=2, bootstrap_samples=100, minimum_subgroup_size=10)


def test_public_aggregates_do_not_contain_row_identifiers(synthetic_frame) -> None:
    truth = synthetic_frame["target"].to_numpy(dtype=int)
    scores = {"logistic_regression": np.linspace(0.1, 0.9, len(truth))}
    leaderboard = build_leaderboard(truth, scores, {"logistic_regression": 0.5}, config())
    subgroups = subgroup_analysis(synthetic_frame, scores, minimum_size=10)
    calibration = calibration_bins(truth, scores["logistic_regression"])
    serialised = json.dumps([leaderboard, subgroups, calibration])
    assert "synthetic-0001" not in serialised
    assert leaderboard[0]["track"] == "classical"


def test_result_and_report_writers_create_traceable_outputs(tmp_path) -> None:
    payload = {
        "experiment": {"experiment_id": "test", "fingerprint": "abc", "folds": 2},
        "dataset": {"cohorts": [{"rows": 20}]},
        "leaderboard": [
            {
                "model": "model",
                "track": "classical",
                "roc_auc": 0.8,
                "roc_auc_interval": {"lower": 0.7, "upper": 0.9},
                "balanced_accuracy": 0.7,
                "brier": 0.2,
                "ece": 0.1,
                "runtime_seconds": 0.2,
            }
        ],
        "primary_comparison": None,
    }
    output = tmp_path / "results.json"
    report = tmp_path / "results.md"
    fingerprint = write_results(payload, output)
    written = json.loads(output.read_text(encoding="utf-8"))
    payload["artefact_sha256"] = fingerprint
    write_markdown_report(payload, report)
    assert len(fingerprint) == 64
    assert written["artefact_sha256"] == fingerprint
    assert "Model Evidence" in report.read_text(encoding="utf-8")
    assert canonical_hash({"a": 1}) == canonical_hash({"a": 1})

