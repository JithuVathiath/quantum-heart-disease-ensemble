# Contributing

Contributions that improve reproducibility, accessibility, validation design, quantum-kernel diagnostics, documentation, or responsible interpretation are welcome.

## Before Opening a Change

1. Describe the research or engineering problem.
2. Keep the historical paper claim separate from newly generated results.
3. Do not add patient-level records, private data, credentials, or unlicensed assets.
4. Add or update tests for behavioural changes.
5. Regenerate public artefacts only from a versioned configuration.

## Local Quality Gate

```bash
ruff check src tests scripts
mypy src
pytest --cov=qheart
python scripts/validate_public_artifact.py artifacts/public/results.json
python scripts/build_technical_report.py
python scripts/build_notebook.py --execute
```

Changes to displayed metrics must include the configuration fingerprint, output fingerprint, environment record, and an explanation in the pull request.
