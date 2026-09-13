PYTHON ?= .venv/bin/python
QHEART ?= .venv/bin/qheart
PNPM ?= pnpm

.PHONY: setup data profile benchmark sync test explorer-build explorer-test all

setup:
	python3.12 -m venv .venv
	.venv/bin/pip install -e '.[dev,quantum]'

data:
	$(QHEART) data download --data-dir data

profile:
	$(QHEART) data profile --data-dir data

benchmark:
	$(QHEART) benchmark --data-dir data --config configs/reference.json --output artifacts/public/results.json --report reports/results.md

sync:
	$(PYTHON) scripts/sync_explorer_results.py

test:
	.venv/bin/ruff check src tests
	.venv/bin/mypy src
	.venv/bin/pytest --cov=qheart

explorer-build:
	$(PNPM) --dir apps/explorer install --frozen-lockfile
	$(PNPM) --dir apps/explorer build

explorer-test:
	$(PNPM) --dir apps/explorer test
	$(PNPM) --dir apps/explorer test:e2e

all: test benchmark sync explorer-build explorer-test
