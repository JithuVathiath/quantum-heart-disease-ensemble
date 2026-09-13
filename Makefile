PYTHON ?= .venv/bin/python
QHEART ?= .venv/bin/qheart

.PHONY: setup data profile benchmark notebook report test all

setup:
	python3.12 -m venv .venv
	.venv/bin/pip install -e '.[dev,notebook,quantum]'

data:
	$(QHEART) data download --data-dir data

profile:
	$(QHEART) data profile --data-dir data

benchmark:
	$(QHEART) benchmark --data-dir data --config configs/reference.json --output artifacts/public/results.json --report reports/results.md

notebook:
	$(PYTHON) scripts/build_notebook.py --execute

report:
	$(PYTHON) scripts/build_technical_report.py

test:
	.venv/bin/ruff check src tests scripts
	.venv/bin/mypy src
	.venv/bin/pytest --cov=qheart

all: test benchmark report notebook
