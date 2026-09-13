"""End-to-end benchmark orchestration."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from qheart.analysis import build_leaderboard, calibration_bins, subgroup_analysis
from qheart.classical import benchmark_classical, cross_cohort_stress_test
from qheart.config import ExperimentConfig
from qheart.data import load_all_cohorts, public_data_profile
from qheart.evaluation import paired_bootstrap_difference
from qheart.quantum import benchmark_quantum
from qheart.reporting import environment_record, revision, write_markdown_report, write_results


def run_reference_benchmark(
    data_dir: str | Path,
    config: ExperimentConfig,
    *,
    include_quantum: bool = True,
) -> dict[str, Any]:
    cohorts = load_all_cohorts(data_dir)
    cleveland = cohorts["cleveland"]
    classical = benchmark_classical(cleveland, config)
    probabilities = dict(classical.probabilities)
    runtimes = dict(classical.runtimes)
    folds = list(classical.folds)
    quantum_diagnostics: list[dict[str, Any]] = []

    if include_quantum:
        quantum = benchmark_quantum(cleveland, config)
        probabilities.update(quantum.probabilities)
        runtimes.update(quantum.runtimes)
        folds.extend(quantum.folds)
        quantum_diagnostics = quantum.diagnostics

    y = cleveland["target"].to_numpy(dtype=int)
    leaderboard = build_leaderboard(y, probabilities, runtimes, config)
    comparison = None
    if "bagged_quantum_kernel_svc" in probabilities:
        comparison = paired_bootstrap_difference(
            y,
            probabilities["bagged_quantum_kernel_svc"],
            probabilities["rbf_svc_4d"],
            samples=config.bootstrap_samples,
            seed=config.seed + 500,
        )

    calibration = {
        name: calibration_bins(y, score) for name, score in probabilities.items()
    }
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "code_revision": revision(),
        "publication_context": {
            "paper_title": (
                "Prediction of Cardiac Disease Using Quantum Enhanced Ensemble Learning Approach"
            ),
            "doi": "10.1109/ICITIIT64777.2025.11041018",
            "reported_accuracy": 0.9016,
            "status": "historical_publication_result_not_reproduced_by_this_repository",
        },
        "experiment": {**config.to_dict(), "fingerprint": config.fingerprint},
        "dataset": public_data_profile(cohorts),
        "environment": environment_record(),
        "leaderboard": leaderboard,
        "fold_metrics": folds,
        "primary_comparison": comparison,
        "quantum_diagnostics": quantum_diagnostics,
        "subgroup_metrics": subgroup_analysis(
            cleveland,
            probabilities,
            minimum_size=config.minimum_subgroup_size,
        ),
        "calibration": calibration,
        "transportability": cross_cohort_stress_test(cohorts, config),
        "limitations": [
            (
                "Small historical cohorts with substantial differences in missingness and "
                "collection context."
            ),
            "Binary target conversion discards ordinal severity information.",
            "Statevector simulation measures an idealised quantum kernel, not hardware advantage.",
            "Subgroup results are descriptive and may be unstable despite minimum-support rules.",
            "Predictive performance does not establish clinical benefit, causality, or safety.",
        ],
    }
    return payload


def generate_public_outputs(
    data_dir: str | Path,
    config_path: str | Path,
    output_json: str | Path,
    report_path: str | Path,
    *,
    include_quantum: bool = True,
) -> dict[str, Any]:
    config = ExperimentConfig.from_json(config_path)
    payload = run_reference_benchmark(data_dir, config, include_quantum=include_quantum)
    fingerprint = write_results(payload, output_json)
    payload["artefact_sha256"] = fingerprint
    write_markdown_report(payload, report_path)
    return payload
