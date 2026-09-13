# Project Plan

## Portfolio Role

**Classification:** Flagship research project  
**Primary signal:** Quantum machine learning, rigorous evaluation, explainability, and reproducible research  
**Academic link:** Bachelor's Major Project at SRM Institute of Science and Technology and IEEE ICITIIT 2025 publication
**Distinct from existing work:** The product is a rigorous quantum-kernel reproduction study, not a clinical prediction form or a single-metric classroom notebook.

## Product Concept

Build a reproducible experiment system, an executed analysis notebook, and a technical report that answer four questions:

1. Can the reported quantum-enhanced approach be reproduced under a fully documented protocol?
2. Does it outperform strong, compute-aware classical baselines beyond split-to-split uncertainty?
3. How sensitive is the conclusion to feature reduction, feature maps, seeds, cohort choice, and missing-data policy?
4. Does performance transfer between hospital cohorts, or is it specific to Cleveland?

The deliverables focus on aggregate research evidence. They do not solicit patient information or display a diagnosis.

## Technical Architecture

### Research Engine

- Python package with typed configuration and deterministic experiment manifests
- UCI acquisition, schema validation, attribution, and checksum verification
- cohort-specific cleaning with missingness and provenance reports
- preprocessing fitted inside each training fold
- classical and quantum-kernel model adapters
- repeated stratified validation and hospital-held-out evaluation
- probability calibration, bootstrap confidence intervals, subgroup slices, and paired comparisons
- structured JSON artefacts consumed by the notebook and reports

### Quantum Track

- Qiskit Machine Learning `FidelityStatevectorKernel` for a deterministic simulator baseline
- optional shot-based `FidelityQuantumKernel` track for sampling sensitivity
- QSVC and bagged QSVC experiments
- fixed and trainable feature-map comparisons where computationally defensible
- cached kernel matrices with data, split, feature-map, and environment fingerprints
- kernel diagnostics: target alignment, eigenvalue spectrum, effective rank, and class separation

### Classical Track

- regularised logistic regression
- linear and RBF support-vector classifiers
- random forest or extra trees
- gradient boosting
- deliberately simple dummy baseline

Classical models will receive the same training folds and evaluation protocol. Hyperparameter searches will be bounded and nested where used.

### Notebook and Report

- executed Python notebook that reads the versioned aggregate artefact
- experiment overview and paper-versus-reproduction boundary
- cohort and missingness profiles
- model leaderboard and confidence-interval forest plot
- calibration, subgroup, and transportability analysis
- quantum-kernel diagnostics and compute-cost interpretation
- comprehensive technical report with reproducibility manifest and limitations

The notebook can be reviewed directly on GitHub and reproduced without a web server or patient-level data.

## Evaluation Design

### Primary Outcomes

- ROC AUC
- balanced accuracy
- sensitivity and specificity
- precision, recall, and F1
- Brier score and expected calibration error

### Reliability Evidence

- repeated stratified cross-validation on Cleveland
- patient-row deduplication checks
- fold-local imputation, scaling, feature selection, and calibration
- bootstrap confidence intervals
- paired fold-level model comparisons
- seed-sensitivity analysis
- cross-hospital transfer matrix

### Subgroup and Error Analysis

- performance by documented demographic attributes where sample size is sufficient
- explicit suppression of unreliable tiny-group estimates
- false-negative and false-positive profile analysis
- missingness sensitivity
- label-definition and cohort-shift discussion

### Quantum-Specific Evidence

- feature-map and qubit-count sensitivity
- kernel-target alignment
- kernel spectrum and effective rank
- simulator runtime and memory use
- shot-count sensitivity for the optional sampled track
- performance per unit of compute

## Repository Structure

```text
quantum-heart-disease-ensemble/
|-- configs/                    # Versioned experiment definitions
|-- data/                       # Ignored raw data and documented sample metadata
|-- docs/                       # Protocol, ethics, architecture, and results
|-- notebooks/                  # Executed research notebook
|-- reports/                    # Generated benchmark and technical reports
|-- scripts/                    # Reproducible acquisition and benchmark commands
|-- src/qheart/                 # Research engine
|-- tests/                      # Unit, integration, determinism, and data-contract tests
|-- Dockerfile
|-- Makefile
|-- pyproject.toml
`-- README.md
```

## Delivery Phases

### Phase 1 - Evidence and Data Foundation

- document the publication and claim boundary;
- write the data card and CC BY 4.0 attribution;
- implement checksum-verified acquisition and schema validation;
- generate cohort, target, duplication, and missingness profiles;
- freeze the first experiment protocol before observing benchmark results.

### Phase 2 - Classical Benchmark

- implement leakage-safe preprocessing and split generation;
- train deterministic classical baselines;
- add calibration, thresholds, confidence intervals, and paired comparisons;
- generate real benchmark artefacts and tests.

### Phase 3 - Quantum Benchmark

- implement statevector quantum kernels and QSVC;
- add bagged QSVC using reproducible bootstrap members;
- cache and fingerprint kernel matrices;
- run sensitivity and compute-cost experiments;
- compare quantum and classical evidence without overclaiming advantage.

### Phase 4 - Generalisation and Interpretation

- add hospital-held-out evaluation;
- analyse subgroup stability, errors, and missingness;
- implement model-appropriate explanations;
- document limitations and threats to validity.

### Phase 5 - Portfolio Publication

- build and execute the analysis notebook;
- generate the comprehensive technical report;
- add architecture and recruiter-ready visuals;
- add Docker, CI, release metadata, citation, and contributor documentation;
- run the full publication gate;
- publish the repository only after all checks pass.

## Publication Gate

The repository must not be published until:

- every displayed metric is generated from committed code and a versioned manifest;
- the historical 90.16% claim is visually separated from reproduction results;
- raw data is either excluded or redistributed strictly under its licence with attribution;
- deterministic smoke tests and the complete classical benchmark pass;
- the quantum path passes on the documented supported environment;
- the notebook executes from the committed aggregate artefact without errors;
- the notebook and report contain no patient-level input or clinical-use implication;
- CI, security checks, licence, citation, limitations, and run instructions are complete.

## Definition of Done

A recruiter can open the notebook or report, understand the research question in under one minute, inspect honest comparative evidence, trace every result to an experiment manifest, and reproduce the reference benchmark from documented commands.
