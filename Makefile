SHELL := /bin/bash

.PHONY: lint
lint:
	isort --check trustml tests && \
	ruff check trustml tests && \
	mypy trustml && \
	bandit -r trustml && \
	interrogate -v --fail-under 50 trustml

.PHONY: lint-fix
lint-fix:
	isort trustml tests

.PHONY: test
test:
	python -m pytest --cov=trustml tests/

.PHONY: docwatch
docwatch:
	sphinx-autobuild docs/source docs/build
