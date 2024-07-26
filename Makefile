SRC_DIR = ./benchmarking
TEST_DIR = ./tests

.PHONY: check fix run

check:
	poetry run mypy --version
	poetry run mypy $(SRC_DIR) $(TEST_DIR)
	poetry run ruff --version
	poetry run ruff check $(SRC_DIR) $(TEST_DIR)
	poetry run black --version
	poetry run black --check $(SRC_DIR) $(TEST_DIR)
	poetry run isort --version
	poetry run isort --check-only $(SRC_DIR) $(TEST_DIR)

fix:
	poetry run black $(SRC_DIR) $(TEST_DIR)
	poetry run isort $(SRC_DIR) $(TEST_DIR)
	poetry run ruff check --fix $(SRC_DIR) $(TEST_DIR)

test:
	poetry run pytest -v $(TEST_DIR)

test-cov:
	poetry run pytest --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html $(TEST_DIR)

show-outdated:
	poetry show --outdated
