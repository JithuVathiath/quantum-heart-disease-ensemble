"""Contract tests for the portfolio-facing notebook and report."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_notebook_is_executed_without_errors() -> None:
    notebook_path = ROOT / "notebooks/quantum_heart_disease_reproduction.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]

    assert len(code_cells) >= 8
    assert all(cell["execution_count"] is not None for cell in code_cells)
    assert not any(
        output.get("output_type") == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )


def test_notebook_uses_aggregate_artefact_and_has_research_boundary() -> None:
    notebook_path = ROOT / "notebooks/quantum_heart_disease_reproduction.ipynb"
    content = notebook_path.read_text(encoding="utf-8")

    assert "artifacts/public/results.json" in content
    assert "90.16%" in content
    assert "not claimed as reproduced" in content
    assert "No Quantum Advantage Was Demonstrated" in content
    assert "Bachelor's Major Project" in content
    assert "researchgate.net/publication/393118567" in content


def test_technical_report_contains_traceable_results() -> None:
    artefact = json.loads((ROOT / "artifacts/public/results.json").read_text(encoding="utf-8"))
    report = (ROOT / "reports/technical-report.md").read_text(encoding="utf-8")

    assert artefact["artefact_sha256"] in report
    assert "0.895 ROC AUC" in report
    assert "does not\ndemonstrate a quantum advantage" in report
    assert "for research, education, and portfolio demonstration only" in report
    assert "SRM Institute of Science and Technology" in report
    assert "researchgate.net/publication/393118567" in report
