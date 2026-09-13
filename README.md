# Quantum-Enhanced Heart Disease Ensemble

An open, reproducible research companion to the 2025 IEEE ICITIIT paper **"Prediction of Cardiac Disease Using Quantum Enhanced Ensemble Learning Approach"** by Jithu Vathiath Biju, Adithya P. Mallya, and P. Kirubanantham.

This project will evaluate when a bagged quantum-kernel classifier helps, when it does not, and how stable its conclusions remain across validation designs and hospital cohorts. It is a research and education project, not a clinical diagnostic tool.

## Why This Repository Exists

The original undergraduate study reported 90.16% accuracy on the Cleveland heart-disease dataset using a Quantum Support Vector Classifier ensemble and SHAP-based interpretation. This repository will keep that published result visibly separate from all newly executed results while providing:

- a leakage-safe reproduction protocol;
- transparent classical and quantum-kernel baselines;
- uncertainty, calibration, subgroup, and error analysis;
- cross-hospital generalisation experiments;
- compute-cost and kernel-quality evidence;
- an interactive experiment explorer;
- tested commands, containers, continuous integration, and traceable artefacts.

## Planned Research Tracks

1. **Published Study Context** - accurately document the paper, authorship, dataset, reported method, and reported result.
2. **Cleveland Reproduction** - execute a preregistered, leakage-safe benchmark on the Cleveland cohort.
3. **Cross-Hospital Stress Test** - evaluate transportability across the Cleveland, Hungarian, Switzerland, and Long Beach VA cohorts where data quality permits.
4. **Quantum Kernel Observatory** - inspect feature maps, kernel matrices, alignment, effective dimension, runtime, and sensitivity to noise or sampling.
5. **Evidence Explorer** - compare models, folds, cohorts, uncertainty intervals, calibration, subgroup slices, explanations, and compute cost in a public web interface.

## Evidence Boundary

The published 90.16% accuracy is a historical paper result. It will not be presented as a newly reproduced result unless the exact protocol is executed successfully. New experiments will have their own versioned manifests, seeds, data hashes, environment details, and generated reports.

## Data

The project will use the UCI Heart Disease dataset (DOI: `10.24432/C52P4X`), which is licensed under CC BY 4.0. Raw downloads will remain outside Git history; the repository will provide a documented, checksum-verified acquisition step and attribution.

## Current Status

The research protocol and delivery plan are being established locally. The repository will remain unpublished until its benchmark, tests, documentation, and interactive explorer pass the publication gate.

See [Project Plan](docs/project-plan.md) and [Research Protocol](docs/research-protocol.md).

## Responsible-Use Notice

This software is for research, education, and portfolio demonstration only. It must not be used to diagnose disease, make treatment decisions, or replace qualified medical judgement. The underlying datasets are small, historical, heterogeneous, and unsuitable for unvalidated clinical deployment.

