.DEFAULT_GOAL := install

UV ?= uv
ARGS ?=

.PHONY: install run debug clean lint

install:
	$(UV) sync

run:
	$(UV) run python -m src $(ARGS)

debug:
	$(UV) run python -m pdb -m src $(ARGS)

clean:
	find . \( -path './.git' -o -path './.venv' -o -path './data' \
		-o -path './models' -o -path './output' -o -path './outputs' \
		-o -path './.cache' -o -path './.uv-cache' \
		-o -path './.huggingface' -o -path './.hf-cache' \) -prune -o \
		-type d \( -name '__pycache__' -o -name '.mypy_cache' \
		-o -name '.pytest_cache' -o -name '.ruff_cache' \) \
		-prune -exec rm -rf {} + -o \
		-type f \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -f {} +

lint:
	$(UV) run flake8 .
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
