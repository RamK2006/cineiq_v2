.PHONY: download-data train build-embeddings dev test lint migrate build clean

download-data:
	@echo "Downloading MovieLens 25M dataset..."
	python data_pipeline/download_movielens.py

ingest-tmdb:
	@echo "Ingesting TMDB movie data..."
	python data_pipeline/ingest_tmdb.py

train:
	@echo "Training ML models (SVD + NCF)..."
	python backend/app/ml/train_svd.py
	python backend/app/ml/train_ncf.py

build-embeddings:
	@echo "Generating vector embeddings for Qdrant..."
	python data_pipeline/generate_embeddings.py

migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

dev:
	@echo "Starting all services..."
	docker-compose up

dev-build:
	@echo "Building and starting all services..."
	docker-compose up --build

test:
	@echo "Running backend tests..."
	cd backend && pytest --cov=app --cov-report=html
	@echo "Running frontend tests..."
	cd frontend && npm test

lint:
	@echo "Linting backend..."
	cd backend && ruff check app/
	cd backend && mypy app/
	@echo "Linting frontend..."
	cd frontend && npm run lint

build:
	@echo "Building Docker images..."
	docker-compose build

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf backend/app/ml/models/*.pkl
	rm -rf backend/app/ml/models/*.pt
	rm -rf data/ml-25m/

setup: download-data migrate ingest-tmdb train build-embeddings
	@echo "Setup complete! Run 'make dev' to start the application."
