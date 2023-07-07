SHELL := /bin/bash

.PHONY: lint
lint:
	isort --check trustml tests && \
	flake8 --show-source --statistics trustml tests && \
	mypy trustml && \
	bandit -r trustml && \
	interrogate --fail-under 50 trustml

.PHONY: fix-lint
fix-lint:
	isort trustml tests

.PHONY: test
test:
	python -m pytest --cov=trustml tests/

.PHONY: docwatch
docwatch:
	sphinx-autobuild docs/source docs/build

