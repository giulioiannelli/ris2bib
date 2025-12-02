PYTHON ?= python3

.PHONY: install dev test lint clean

install:
	$(PYTHON) -m pip install .

dev:
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m compileall src

clean:
	rm -rf build dist .pytest_cache *.egg-info
