# Responsible-Use Statement

## Core Boundary

Quantum Heart is an evidence explorer, not a healthcare product. It intentionally provides no patient-input form, no individual risk estimate, and no diagnostic recommendation.

## Why This Matters

The dataset contains historical clinical variables, which can make a polished interface appear medically authoritative. That impression would be unsafe. Good predictive performance on a small retrospective dataset does not demonstrate clinical benefit, calibration in a new population, causal validity, safety, or regulatory readiness.

## Safeguards

- patient-level source records remain outside Git;
- public artefacts contain aggregates only;
- the published paper result is separated from the new benchmark;
- subgroup estimates below the declared support threshold are suppressed;
- diagonal cross-cohort cells are labelled as apparent fit;
- limitations are visible in the primary interface;
- runtime evidence is labelled as statevector simulation, not hardware speed-up;
- all run instructions and manifests are versioned.

## Prohibited Uses

Do not use this repository to diagnose or screen a person, recommend treatment or healthcare access, make insurance or employment decisions, infer sensitive medical information about an identifiable person, claim medical-device performance, or claim quantum advantage beyond the exact evidence displayed.

## Reporting Concerns

Open a GitHub issue for reproducibility errors, misleading wording, data-attribution problems, accessibility defects, or security concerns that do not expose private information. Use the private process in [`../SECURITY.md`](../SECURITY.md) for vulnerabilities.

