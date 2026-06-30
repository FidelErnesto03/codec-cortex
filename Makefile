# CODEC-CORTEX CLI — Makefile
# Targets: install, test, lint, build, publish, clean

SHELL := /bin/bash

.PHONY: install test lint build publish clean

install:
	pip install -e cli/[dev]

test:
	cd cli && python -m pytest src/tests/ -q

lint:
	cd cli && ruff check src/

build:
	cd cli && python -m build --wheel

publish: build
	cd cli && twine upload dist/*

clean:
	cd cli && rm -rf dist/ build/ *.egg-info
	find cli/src -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	find cli/src -name "*.pyc" -delete 2>/dev/null || true

verify:
	cd cli && cortex verify --strict ../skill/cortex/SKILL.md

roundtrip:
	cd cli && cortex v2-roundtrip-bidir ../skill/cortex/SKILL.md

all: install lint test verify roundtrip
