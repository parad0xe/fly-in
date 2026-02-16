# structure
MAIN := fly_in.py
ARGS ?= 

VENV := .venv
VENV_STATE := $(VENV)/.install

POETRY_LOCK := poetry.lock
PYPROJECT_TOML := pyproject.toml

# cache
CACHE_DIRS := __pycache__ .mypy_cache .pytest_cache
CACHE_EXCLUDE = -name "$(VENV)" -prune -o
CACHE_SEARCH = $(foreach cache,$(CACHE_DIRS),-name "$(cache)" -o)
FIND_CACHES = find . \
	$(CACHE_EXCLUDE) \
	-type d \( $(CACHE_SEARCH) -false \) -print

# tools
PYTHON := $(VENV)/bin/python3
FLAKE8 := $(PYTHON) -m flake8 --exclude $(VENV)
MYPY := $(PYTHON) -m mypy --exclude $(VENV)
PYTEST := $(PYTHON) -m pytest
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
	$(FIND_CACHES) -exec rm -rf {} + 1>/dev/null
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

tests: install
	@$(PYTEST)

$(PYTHON):
	@python3 -m venv $(VENV)
	@$(PIP) install -U pip poetry

# miscellaneous
.PHONY: install run debug lint lint-strict clean
