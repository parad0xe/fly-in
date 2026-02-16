# structure
MAIN := fly_in.py
ARGS ?= 

VENV := .venv
VENV_STATE := $(VENV)/.install

SRC_DIRS := .

POETRY_LOCK := poetry.lock
PYPROJECT_TOML := pyproject.toml

PYCACHES = $(addsuffix /__pycache__,$(SRC_DIRS))
MYPYCACHES = $(addsuffix /.mypy_cache,$(SRC_DIRS))
EXCLUDE = --exclude $(VENV)

# tools
PYTHON := $(VENV)/bin/python3
FLAKE8 := $(PYTHON) -m flake8 $(EXCLUDE)
MYPY := $(PYTHON) -m mypy $(EXCLUDE)
PIP := $(PYTHON) -m pip
POETRY := POETRY_VIRTUALENVS_IN_PROJECT=true $(PYTHON) -m poetry

# rules
install: $(POETRY_LOCK) $(VENV_STATE) | $(PYTHON)

run: install | $(PYTHON)
	$(PYTHON) $(MAIN) $(ARGS)

$(POETRY_LOCK) $(VENV_STATE) &: $(PYPROJECT_TOML) | $(PYTHON)
	@$(POETRY) lock
	@$(POETRY) install --with dev --no-root
	@touch $(POETRY_LOCK) $(VENV_STATE)

clean:
	rm -rf $(PYCACHES) $(MYPYCACHES)
	rm -rf $(VENV)

debug: install
	$(PYTHON) -m pdb $(MAIN) $(ARGS)

lint: install
	@$(FLAKE8)
	@$(MYPY) . --check-untyped-defs \
	--warn-unused-ignores --ignore-missing-imports \
	--warn-return-any --disallow-untyped-defs

lint-strict: install
	@$(FLAKE8)
	@$(MYPY) . --strict

$(PYTHON):
	@python3 -m venv $(VENV)
	@$(PIP) install -U pip poetry

# miscellaneous
.PHONY: install run debug lint lint-strict clean
