
VENV_PYTHON=.venv/bin/python

.PHONY: lint

all: lint

lint:
	black annotator/* test/*