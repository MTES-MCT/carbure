.PHONY: \
	up down restart logs-django_cmd open restart-backend restart-frontend \
	test-backend test-frontend \
	makemigrations migrate seed ipython \
	lint-fix translate translate-missing \
	check-diff check-types generate-and-check-types \
	flush

-include .env
export

docker_compose ?= docker-compose.yml
module ?= web
context ?=

docker_cmd ?= docker compose -f $(docker_compose)
django_cmd ?= uv run python web/manage.py
npm_cmd ?= npm --prefix front

# Docker
build:
	$(docker_cmd) build

up:
	$(docker_cmd) up -d

down:
	$(docker_cmd) down

restart:
	$(docker_cmd) down && $(docker_cmd) up -d

restart-backend:
	$(docker_cmd) restart carbure-django

restart-frontend:
	$(docker_cmd) restart carbure-frontend

open:
	open http://carbure.local:8090/

# Tests
test-backend:
	$(django_cmd) test --keepdb $(module)

test-frontend:
	$(npm_cmd) test

# Backend
makemigrations:
	$(django_cmd) makemigrations

migrate:
	$(django_cmd) migrate

seed:
	$(django_cmd) create_sample_data $(app)

ipython:
	$(django_cmd) shell --interface ipython

# Frontend
lint:
	$(npm_cmd) run lint

lint-fix:
	$(npm_cmd) run lint:fix

translate:
	$(npm_cmd) run translate

translate-missing:
	$(npm_cmd) run translate-missing -- $(context)

# Type checking
generate-and-check-types:
	$(django_cmd) spectacular --file api-schema.yaml
	$(npm_cmd) run generate-api
	$(npm_cmd) run check-diff
	$(npm_cmd) run check-types

check-diff:
	$(npm_cmd) run check-diff

check-types:
	$(npm_cmd) run check-types

flush:
	$(django_cmd) flush