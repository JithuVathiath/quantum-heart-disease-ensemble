# Data Card

## Dataset Identity

- **Name:** UCI Heart Disease
- **DOI:** `10.24432/C52P4X`
- **Original creators:** Andras Janosi, William Steinbrunn, Matthias Pfisterer, and Robert Detrano
- **Licence:** Creative Commons Attribution 4.0 International
- **Source used:** official UCI archive at `https://archive.ics.uci.edu/static/public/45/heart+disease.zip`
- **Acquisition manifest:** [`../data/manifest.json`](../data/manifest.json)

## Intended Use in This Project

The dataset supports a methodological reproduction and transportability stress test. It is not used to build or validate a medical device. The primary experiment uses the Cleveland processed cohort. Secondary experiments train and test classical baselines across four hospital cohorts using the common feature subset.

## Observed Cohort Profile

| Cohort | Rows | Positive | Positive Rate | Missing Feature Cells | Duplicate Rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cleveland | 303 | 139 | 45.9% | 6 | 0 |
| Hungarian | 294 | 106 | 36.1% | 782 | 1 |
| Switzerland | 123 | 115 | 93.5% | 273 | 0 |
| Long Beach VA | 200 | 149 | 74.5% | 698 | 1 |
| **Total** | **920** | **509** | - | **1,759** | **2** |

These figures were generated from the checksum-verified archive by `qheart data profile`.

## Features and Target

The processed files contain 13 commonly used features: age, sex, chest-pain type, resting blood pressure, cholesterol, fasting blood sugar, resting ECG, maximum heart rate, exercise-induced angina, ST depression, slope, major-vessel count, and thal status.

The UCI `num` field is converted to a binary target: `0` remains absence, and values greater than `0` become presence. This transformation discards ordinal severity and is recorded in every experiment manifest.

## Missingness

Missingness is not uniform. The `ca` and `thal` fields are largely absent outside Cleveland, while several Long Beach VA measurements also have substantial gaps. The primary benchmark uses fold-local imputation. The cross-cohort test excludes `ca` and `thal` but retains the remaining missingness as a realistic stressor.

## Known Risks

- The cohorts are historical and may not represent present-day populations or clinical practice.
- Collection sites differ in prevalence, measurement availability, and likely referral patterns.
- The binary target does not describe time horizon, treatment, or causal mechanism.
- Small subgroup counts can produce unstable estimates.
- Duplicate-feature records exist in two cohorts and are disclosed rather than silently removed.
- Protected attributes are incomplete; subgroup analysis is descriptive, not a fairness certification.

## Distribution Policy

Raw records and extracted files are excluded from Git. The repository distributes only source and licence metadata, cryptographic file hashes, aggregate cohort profiles, and aggregate model evaluation artefacts.

Users retrieve the source directly from UCI and remain responsible for observing CC BY 4.0 attribution requirements.
