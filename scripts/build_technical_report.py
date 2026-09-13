"""Generate the comprehensive technical report from the public evidence artefact."""

# ruff: noqa: E501

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTEFACT = ROOT / "artifacts/public/results.json"
REPORT = ROOT / "reports/technical-report.md"

MODEL_LABELS = {
    "logistic_regression": "Logistic Regression",
    "extra_trees": "Extra Trees",
    "rbf_svc": "RBF-SVC (Full)",
    "hist_gradient_boosting": "Histogram Gradient Boosting",
    "rbf_svc_4d": "RBF-SVC (Matched 4D)",
    "bagged_quantum_kernel_svc": "Bagged Quantum-Kernel SVC",
    "quantum_kernel_svc": "Quantum-Kernel SVC",
    "dummy_prior": "Dummy Prior",
}
COHORTS = ["cleveland", "hungarian", "switzerland", "long-beach-va"]


def cohort_label(value: str) -> str:
    """Return a presentation label for a cohort slug."""
    labels = {
        "long-beach-va": "Long Beach VA",
        "sex_female": "Female",
        "sex_male": "Male",
        "age_under_60": "Age Under 60",
        "age_60_or_over": "Age 60 or Over",
    }
    return labels.get(value, value.replace("-", " ").title())


def transport_table(records: list[dict[str, Any]], model: str) -> str:
    """Render one cross-cohort ROC AUC matrix as Markdown."""
    lookup = {
        (record["train_cohort"], record["test_cohort"]): record
        for record in records
        if record["model"] == model
    }
    header = "| Train \\ Test | " + " | ".join(cohort_label(item) for item in COHORTS) + " |"
    separator = "| --- | " + " | ".join("---:" for _ in COHORTS) + " |"
    rows = []
    for train in COHORTS:
        values = []
        for test in COHORTS:
            record = lookup[(train, test)]
            suffix = "*" if record["validation_type"] == "resubstitution" else ""
            values.append(f"{record['roc_auc']:.3f}{suffix}")
        rows.append(f"| {cohort_label(train)} | " + " | ".join(values) + " |")
    return "\n".join([header, separator, *rows])


def build_report(evidence: dict[str, Any]) -> str:
    """Render the technical report as Markdown."""
    leaderboard = evidence["leaderboard"]
    comparison = evidence["primary_comparison"]
    diagnostics = evidence["quantum_diagnostics"]
    experiment = evidence["experiment"]
    environment = evidence["environment"]

    cohort_rows = []
    for cohort in evidence["dataset"]["cohorts"]:
        cohort_rows.append(
            f"| {cohort_label(cohort['cohort'])} | {cohort['rows']} | "
            f"{cohort['positive_rate']:.1%} | {cohort['missing_cells']} | "
            f"{cohort['duplicate_rows']} |"
        )

    leaderboard_rows = []
    for record in leaderboard:
        interval = record["roc_auc_interval"]
        leaderboard_rows.append(
            f"| {MODEL_LABELS[record['model']]} | {record['track'].title()} | "
            f"{record['roc_auc']:.3f} ({interval['lower']:.3f}-{interval['upper']:.3f}) | "
            f"{record['balanced_accuracy']:.3f} | {record['brier']:.3f} | "
            f"{record['ece']:.3f} | {record['runtime_seconds']:.2f} |"
        )

    diagnostic_rows = []
    for record in diagnostics:
        diagnostic_rows.append(
            f"| {record['fold'] + 1} | {record['kernel_target_alignment']:.3f} | "
            f"{record['effective_rank']:.1f} | {record['condition_proxy']:,.0f} | "
            f"{record['kernel_seconds']:.3f} |"
        )

    subgroup_rows = []
    for record in evidence["subgroup_metrics"]:
        if record["model"] not in {"logistic_regression", "bagged_quantum_kernel_svc"}:
            continue
        subgroup_rows.append(
            f"| {MODEL_LABELS[record['model']]} | {cohort_label(record['group'])} | "
            f"{record['rows']} | {record['positive_rows']} | {record['roc_auc']:.3f} | "
            f"{record['balanced_accuracy']:.3f} | {record['brier']:.3f} |"
        )

    limitations = "\n".join(f"- {item}" for item in evidence["limitations"])
    logistic_transport = transport_table(evidence["transportability"], "logistic_regression")
    rbf_transport = transport_table(evidence["transportability"], "rbf_svc")

    return f"""# Quantum-Enhanced Heart Disease Ensemble: Technical Report

**Report status:** Generated from the versioned public evidence artefact  
**Academic designation:** Bachelor's Major Project — SRM Institute of Science and Technology<br>
**Experiment:** `{experiment["experiment_id"]}`  
**Artefact SHA-256:** `{evidence["artefact_sha256"]}`  
**Associated paper:** [IEEE DOI {evidence["publication_context"]["doi"]}](https://doi.org/{evidence["publication_context"]["doi"]})  
**ResearchGate:** [Prediction of Cardiac Disease Using Quantum Enhanced Ensemble Learning Approach](https://www.researchgate.net/publication/393118567_Prediction_of_Cardiac_Disease_Using_Quantum_Enhanced_Ensemble_Learning_Approach)<br>
**Dataset:** [UCI Heart Disease, DOI {evidence["dataset"]["dataset_doi"]}](https://doi.org/{evidence["dataset"]["dataset_doi"]}), {evidence["dataset"]["licence"]}

## Executive Summary

This study re-examines a quantum-enhanced ensemble approach to cardiac-disease classification
under a frozen, leakage-safe, and uncertainty-aware protocol. The strongest model was logistic
regression at **{leaderboard[0]["roc_auc"]:.3f} ROC AUC**. The bagged quantum-kernel SVC reached
**{next(item for item in leaderboard if item["model"] == "bagged_quantum_kernel_svc")["roc_auc"]:.3f} ROC AUC**.
Against the compute-matched four-component RBF-SVC, its paired difference was
**{comparison["estimate"]:+.3f}** (95% bootstrap interval
**{comparison["lower"]:+.3f} to {comparison["upper"]:+.3f}**). The evidence therefore does not
demonstrate a quantum advantage under the declared protocol.

This negative result is scientifically useful. It replaces an isolated accuracy headline with a
traceable comparison of discrimination, calibration, subgroup behaviour, kernel geometry,
runtime, and cross-hospital transportability.

## Publication Claim and Reproduction Boundary

The associated 2025 paper reported **{evidence["publication_context"]["reported_accuracy"]:.2%}
accuracy** on the Cleveland dataset. That value is retained as historical publication context,
not presented as reproduced. The exact original split and implementation artefacts were not
available here. All numbers in this report were newly generated by the repository's declared
reference protocol and can be traced to the public JSON artefact.

## Research Questions

1. How does the quantum-kernel ensemble compare with strong classical baselines?
2. Does it outperform an RBF-SVC receiving the same four-component representation?
3. Are predicted probabilities well calibrated and errors stable across documented subgroups?
4. How well do classical conclusions transfer between the four UCI hospital cohorts?
5. Do quantum-kernel diagnostics help explain observed predictive performance?

## Data

The UCI Heart Disease collection contains **{evidence["dataset"]["total_rows"]} rows** and
**{evidence["dataset"]["feature_count"]} model features** across four hospital cohorts. Raw patient
rows are not committed to Git. The acquisition command downloads the official archive, rejects
unsafe ZIP paths, validates the schema, and records SHA-256 hashes in `data/manifest.json`.

| Cohort | Rows | Positive Rate | Missing Cells | Duplicate Rows |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(cohort_rows)}

The prevalence and missingness differences are substantial. Switzerland's positive rate is
93.5%, and the Hungarian and Long Beach VA cohorts have hundreds of missing feature cells. These
conditions make cross-hospital results a transport stress test rather than clinical validation.

## Methods

### Reference Evaluation

- **Primary cohort:** Cleveland ({next(item["rows"] for item in evidence["dataset"]["cohorts"] if item["cohort"] == "cleveland")} records)
- **Validation:** {experiment["folds"]}-fold stratified out-of-fold evaluation
- **Uncertainty:** {experiment["bootstrap_samples"]} deterministic bootstrap resamples
- **Seed:** `{experiment["seed"]}`
- **Preprocessing:** fold-local imputation, encoding, scaling, and representation fitting
- **Quantum representation:** {experiment["quantum_features"]} components, {experiment["quantum_features"]} qubits,
  ZZ feature map with {experiment["quantum_feature_map_reps"]} repetitions and {experiment["quantum_entanglement"]} entanglement
- **Bagging:** {experiment["bagging_estimators"]} quantum-kernel SVC members

The primary classical comparator is not the full-feature RBF-SVC. It is the four-component
RBF-SVC, because it receives the same fold-local representation as the quantum models. This makes
the central comparison more informative than an unconstrained algorithm leaderboard.

### Metrics

ROC AUC is the primary ranking metric. Balanced accuracy, sensitivity, specificity, precision,
recall, F1, Brier score, expected calibration error, confusion counts, and runtime provide
complementary evidence. All confidence intervals reported below are empirical bootstrap intervals.

## Benchmark Results

| Model | Track | ROC AUC (95% CI) | Balanced Accuracy | Brier | ECE | Runtime (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(leaderboard_rows)}

![Model ROC AUC forest plot](figures/model_auc_forest.png)

Logistic regression and Extra Trees were effectively tied in discrimination, with overlapping
intervals. Logistic regression achieved the lowest Brier score among the evaluated non-dummy
models, while Extra Trees led balanced accuracy. The quantum models performed above the dummy
prior but well below both the full and matched classical alternatives.

## Primary Matched Comparison

The bagged quantum-kernel SVC minus matched four-component RBF-SVC ROC AUC difference was
**{comparison["estimate"]:+.3f}** (95% interval **{comparison["lower"]:+.3f} to
{comparison["upper"]:+.3f}**). The bootstrap probability that the quantum model was better was
**{comparison["probability_first_better"]:.1%}**. The entire interval lies below zero, so this
experiment favours the matched classical baseline.

Bagging improved the single quantum-kernel SVC only modestly. It did not close the much larger
gap to the matched RBF model.

## Calibration and Threshold Behaviour

![Out-of-fold calibration curves](figures/calibration_curves.png)

The full RBF-SVC had the lowest expected calibration error ({next(item["ece"] for item in leaderboard if item["model"] == "rbf_svc"):.3f}),
while logistic regression combined strong discrimination with a Brier score of
{leaderboard[0]["brier"]:.3f}. Calibration curves are descriptive: several bins contain few
records, particularly at extreme predicted probabilities. No probability from this historical
dataset should be interpreted as a clinically validated risk estimate.

## Quantum-Kernel Diagnostics

| Fold | Target Alignment | Effective Rank | Condition Proxy | Kernel Time (s) |
| ---: | ---: | ---: | ---: | ---: |
{chr(10).join(diagnostic_rows)}

![Quantum-kernel diagnostics](figures/quantum_kernel_diagnostics.png)

Mean kernel-target alignment was **{mean(item["kernel_target_alignment"] for item in diagnostics):.3f}**,
and mean effective rank was **{mean(item["effective_rank"] for item in diagnostics):.1f}**. The weak
alignment indicates that the encoded quantum similarity structure has limited correspondence with
the observed class structure. This offers a plausible geometric explanation for the predictive
gap; it is an interpretation, not a causal proof.

The statevector kernel ran on an ideal simulator. Its runtime and accuracy do not establish
hardware speed-up, noise resilience, or computational advantage.

## Cross-Hospital Transportability

Diagonal values marked with `*` are resubstitution scores and represent apparent fit, not external
validation. Off-diagonal cells are the relevant transport stress tests.

### Logistic Regression

{logistic_transport}

### Full RBF-SVC

{rbf_transport}

![Cross-cohort ROC AUC matrices](figures/transportability_matrix.png)

The classical models often transported reasonably from Cleveland to Hungarian, but performance
weakened on Switzerland and Long Beach VA. The most severe case was an RBF-SVC trained on
Switzerland and tested on Cleveland (0.500 ROC AUC), despite perfect apparent fit on Switzerland.
This contrast illustrates why same-cohort performance cannot substitute for external validation.

## Subgroup Audit

| Model | Group | Rows | Positive Rows | ROC AUC | Balanced Accuracy | Brier |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(subgroup_rows)}

The subgroup analysis is descriptive and restricted to groups meeting a minimum support of
{experiment["minimum_subgroup_size"]} records. The bagged quantum model was particularly weak in
the age-60-or-over group (approximately chance-level ROC AUC). These results do not establish
fairness, absence of harm, or demographic validity because the sample is small, historical, and
not representative of a target clinical population.

## Threats to Validity

{limitations}

Additional threats include multiple model comparisons, a single frozen hyperparameter protocol,
binary reduction of the original disease-severity target, and potential site-specific measurement
practices. Apparent-fit transport diagonal values are intentionally labelled to prevent them from
being mistaken for validation evidence.

## Reproducibility Record

| Item | Recorded Value |
| --- | --- |
| Experiment fingerprint | `{experiment["fingerprint"]}` |
| Artefact fingerprint | `{evidence["artefact_sha256"]}` |
| Code revision at benchmark time | `{evidence["code_revision"]}` |
| Python | {environment["python"]} |
| NumPy | {environment["numpy"]} |
| pandas | {environment["pandas"]} |
| scikit-learn | {environment["scikit_learn"]} |
| Qiskit | {environment["qiskit"]} |
| Qiskit Machine Learning | {environment["qiskit_machine_learning"]} |
| Platform | {environment["platform"]} |

To regenerate the complete benchmark:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,notebook,quantum]'
qheart data download --data-dir data
qheart benchmark --data-dir data --config configs/reference.json --output artifacts/public/results.json --report reports/results.md
python scripts/build_technical_report.py
python scripts/build_notebook.py --execute
python scripts/validate_public_artifact.py artifacts/public/results.json
pytest --cov=qheart
```

## Conclusion

Under the frozen protocol, the proposed quantum-kernel ensemble did not outperform a
compute-matched classical RBF-SVC, and logistic regression produced the strongest overall
discrimination. The result should not be generalised beyond these historical cohorts. The
project's contribution is the reproducible evidence system: lawful data acquisition,
leakage-controlled evaluation, paired uncertainty, calibration, kernel diagnostics, subgroup
auditing, transportability analysis, and a transparent negative finding.

This software and report are for research, education, and portfolio demonstration only. They must
not be used to diagnose disease, select treatment, or assess an identifiable person.
"""


def main() -> None:
    """Read the artefact and write the generated report."""
    with ARTEFACT.open(encoding="utf-8") as stream:
        evidence: dict[str, Any] = json.load(stream)
    REPORT.write_text(build_report(evidence), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
