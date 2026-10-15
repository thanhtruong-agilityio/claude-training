.PHONY: up down logs test test-backend test-frontend backup

up: ## build and start BE (:8000) + FE (:5173), localhost only
	docker compose up --build

down: ## stop and remove containers
	docker compose down

logs: ## follow logs
	docker compose logs -f

test: test-backend test-frontend ## run all tests in containers

test-backend:
	docker compose run --rm --no-deps backend uv run pytest

test-frontend:
	docker compose run --rm --no-deps frontend npm test

backup: ## copy the database to backups/clinic-<timestamp>.db
	@mkdir -p backups
	cp backend/clinic.db backups/clinic-$$(date +%Y%m%d-%H%M%S).db
