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

DB ?= backend/clinic.db
BACKUP_DIR ?= backups

backup: ## snapshot the database to backups/clinic-<timestamp>.db and verify it
	@test -f "$(DB)" || { echo "backup failed: $(DB) not found" >&2; exit 1; }
	@mkdir -p "$(BACKUP_DIR)"
	@f="$(BACKUP_DIR)/clinic-$$(date +%Y%m%d-%H%M%S).db"; \
	sqlite3 "$(DB)" ".backup '$$f'" || { rm -f "$$f"; echo "backup failed: could not copy $(DB)" >&2; exit 1; }; \
	r=$$(sqlite3 "$$f" "PRAGMA integrity_check;"); \
	if [ "$$r" != "ok" ]; then rm -f "$$f"; echo "backup failed: integrity check said: $$r" >&2; exit 1; fi; \
	echo "backup ok: $$f"
