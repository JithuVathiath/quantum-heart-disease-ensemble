# Reproduction Benchmark Results

> These are newly executed repository results. The paper's reported 90.16% accuracy is
> historical context and is not claimed as reproduced by this benchmark.

## Reference Protocol

- Experiment: `cleveland-reference-v1`
- Configuration fingerprint: `c2e50c42dc96518b`
- Cohort: Cleveland (303 rows)
- Validation: 5-fold stratified out-of-fold evaluation

## Model Evidence

| Model | Track | ROC AUC (95% CI) | Balanced Accuracy | Brier | ECE | Runtime (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| logistic_regression | classical | 0.895 (0.858-0.928) | 0.809 | 0.129 | 0.050 | 0.06 |
| extra_trees | classical | 0.893 (0.858-0.926) | 0.821 | 0.132 | 0.073 | 0.95 |
| rbf_svc | classical | 0.881 (0.838-0.916) | 0.813 | 0.136 | 0.031 | 0.10 |
| hist_gradient_boosting | classical | 0.869 (0.825-0.908) | 0.784 | 0.155 | 0.095 | 2.31 |
| rbf_svc_4d | classical | 0.856 (0.811-0.897) | 0.785 | 0.152 | 0.047 | 0.07 |
| bagged_quantum_kernel_svc | quantum | 0.661 (0.605-0.721) | 0.598 | 0.235 | 0.083 | 1.80 |
| quantum_kernel_svc | quantum | 0.647 (0.586-0.710) | 0.596 | 0.232 | 0.029 | 1.72 |
| dummy_prior | classical | 0.495 (0.440-0.550) | 0.500 | 0.248 | 0.000 | 0.03 |

## Primary Paired Comparison

Bagged quantum-kernel SVC minus compute-matched RBF-SVC ROC AUC: **-0.194** (95% bootstrap interval -0.256 to -0.133).

## Interpretation Boundary

Performance on these small historical cohorts does not establish clinical utility,
causal validity, safety, or transportability. The report exposes uncertainty,
cohort shift, subgroup support, and compute cost so that a single accuracy value is
never the whole conclusion.

Artefact fingerprint: `f672dbec410768b5b3b5cd2db9cbb049b234650c82192826f77ee81610f731ac`
