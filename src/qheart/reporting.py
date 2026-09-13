"""Versioned public artefacts and a human-readable benchmark report."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn


def revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unavailable"


def environment_record() -> dict[str, str]:
    record = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
    }
    try:
        import qiskit
        import qiskit_machine_learning

        record["qiskit"] = qiskit.__version__
        record["qiskit_machine_learning"] = qiskit_machine_learning.__version__
    except ImportError:
        record["qiskit"] = "not-installed"
        record["qiskit_machine_learning"] = "not-installed"
    return record


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def write_results(payload: dict[str, Any], path: str | Path) -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(payload)
    fingerprint = canonical_hash(payload)
    payload["artefact_sha256"] = fingerprint
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fingerprint


def write_markdown_report(payload: dict[str, Any], path: str | Path) -> None:
    leaderboard = payload["leaderboard"]
    lines = [
        "# Reproduction Benchmark Results",
        "",
        "> These are newly executed repository results. The paper's reported 90.16% accuracy is",
        "> historical context and is not claimed as reproduced by this benchmark.",
        "",
        "## Reference Protocol",
        "",
        f"- Experiment: `{payload['experiment']['experiment_id']}`",
        f"- Configuration fingerprint: `{payload['experiment']['fingerprint']}`",
        f"- Cohort: Cleveland ({payload['dataset']['cohorts'][0]['rows']} rows)",
        f"- Validation: {payload['experiment']['folds']}-fold stratified out-of-fold evaluation",
        "",
        "## Model Evidence",
        "",
        "| Model | Track | ROC AUC (95% CI) | Balanced Accuracy | Brier | ECE | Runtime (s) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in leaderboard:
        interval = row["roc_auc_interval"]
        lines.append(
            "| {model} | {track} | {roc_auc:.3f} ({lower:.3f}-{upper:.3f}) | "
            "{balanced_accuracy:.3f} | {brier:.3f} | {ece:.3f} | {runtime_seconds:.2f} |".format(
                lower=interval["lower"], upper=interval["upper"], **row
            )
        )
    comparison = payload.get("primary_comparison")
    if comparison:
        lines.extend(
            [
                "",
                "## Primary Paired Comparison",
                "",
                (
                    "Bagged quantum-kernel SVC minus compute-matched RBF-SVC ROC AUC: "
                    f"**{comparison['estimate']:+.3f}** "
                    f"(95% bootstrap interval {comparison['lower']:+.3f} to "
                    f"{comparison['upper']:+.3f})."
                ),
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "Performance on these small historical cohorts does not establish clinical utility,",
            "causal validity, safety, or transportability. The report exposes uncertainty,",
            "cohort shift, subgroup support, and compute cost so that a single accuracy value is",
            "never the whole conclusion.",
            "",
            f"Artefact fingerprint: `{payload['artefact_sha256']}`",
            "",
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
