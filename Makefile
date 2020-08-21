
VENV_PYTHON=.venv/bin/python

.PHONY: lint

.venv:
	python3 -m venv .venv --system-site-packages
	pip install -r requirements.txt
all: lint

lint:
	black scraper/* test/*