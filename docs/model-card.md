# Model Card

## System Purpose

This repository compares classical classifiers and quantum-kernel support-vector classifiers on historical UCI Heart Disease cohorts. Its purpose is reproducibility research, model evaluation education, and transparent comparison—not diagnosis.

## Evaluated Models

- prior-only dummy classifier;
- class-weighted logistic regression;
- RBF support-vector classifier using the full encoded representation;
- RBF support-vector classifier using the same four fold-local PCA components as the quantum models;
- Extra Trees ensemble;
- histogram gradient boosting;
- four-qubit Qiskit fidelity statevector kernel SVC;
- seven-member bootstrap ensemble of precomputed quantum-kernel SVCs.

## Primary Protocol

The primary comparison uses five-fold shuffled stratified validation with a fixed seed. All learned preprocessing occurs inside each training fold. Quantum and matched RBF models share the same imputation, encoding, scaling, four-component PCA, and angle-scaling steps.

The quantum feature map uses four qubits, two repetitions, and linear ZZ entanglement. The ideal statevector fidelity kernel is computed once per fold and reused by the single and bagged SVCs.

## Intended Users

- machine-learning and quantum-computing students;
- researchers studying reproducibility and validation design;
- reviewers evaluating Jithu Vathiath Biju's technical portfolio.

## Out-of-Scope Uses

- diagnosis, screening, triage, treatment, insurance, employment, or lending;
- inference about an identifiable person;
- claims of quantum speed-up or hardware advantage;
- clinical deployment or safety certification;
- replacing qualified medical judgement.

## Performance Summary

Logistic regression produced the strongest out-of-fold ROC AUC: 0.895 (95% bootstrap interval 0.858-0.928). The bagged quantum-kernel model produced 0.661 (0.605-0.721). Against the compute-matched four-component RBF-SVC, the paired ROC AUC difference was -0.194 (-0.256 to -0.133).

These results provide evidence against a quantum advantage under this protocol. They do not invalidate the historical paper, whose exact implementation and data split are not claimed to be reproduced.

## Reliability and Error Evidence

The public artefact includes balanced accuracy, sensitivity, specificity, precision, F1, Brier score, expected calibration error, confusion counts, calibration bins, fold metrics, subgroup slices, and cross-cohort ROC AUC.

## Limitations

- Statevector simulation is idealised and classically executed.
- Hyperparameter searches are deliberately bounded; no model is exhaustively optimised.
- Probability estimates from small folds can be unstable.
- Cross-cohort diagonal cells are apparent in-sample fit and are labelled separately.
- External validation is affected by severe feature missingness and prevalence shift.
- No prospective outcomes or clinical utility measures are available.

## Monitoring

There is no deployed prediction service to monitor. Reproducibility is controlled through fixed configuration, file hashes, environment versions, automated tests, and a public artefact fingerprint.
