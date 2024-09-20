all: ruff mypy test
format: ruff
lint: ruff mypy
check: checkblack checkruff

install:
	poetry install --all-extras

ruff:
	poetry run ruff check . --fix

checkruff:
	poetry run ruff check .

mypy:
	poetry run mypy .

test:
	poetry run pytest tests
