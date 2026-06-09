.PHONY: run dev test lint typecheck migrate migrate-down migrate-history docker-build docker-up docker-down clean

run:
	streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0

dev:
	streamlit run app/main.py --server.port=8501 --server.address=127.0.0.1 --server.runOnSave=true

test:
	pytest tests/ -v --tb=short

lint:
	ruff check app/ tests/

typecheck:
	mypy app/ --ignore-missing-imports

migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

migrate-history:
	alembic history --verbose

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
