#!make
SHELL := /bin/bash

# set variable IMAGE_NAME_BACKEND
IMAGE_NAME_BACKEND=data-copilot-backend
IMAGE_NAME_RQ_WORKER=data-copilot-rq-worker
IMAGE_NAME_NGINX=data-copilot-nginx
IMAGE_NAME_CELERY_WORKER=data-copilot-celery-worker
IMAGE_NAME_CELERY_FLOWER=data-copilot-celery-flower
IMAGE_NAME_FRONTEND=data-copilot-frontend

# docker build makefile
build-backend:
	DOCKER_BUILDKIT=1 docker build -t $(IMAGE_NAME_BACKEND) -f dockerfiles/backend/Dockerfile .

build-celery-worker:
	DOCKER_BUILDKIT=1 docker build -t $(IMAGE_NAME_CELERY_WORKER) -f dockerfiles/celery-worker/Dockerfile .

build-celery-flower:
	docker build -t $(IMAGE_NAME_CELERY_FLOWER) -f dockerfiles/flower/Dockerfile .

build-frontend-dev:
	docker build -t $(IMAGE_NAME_FRONTEND)-dev -f dockerfiles/frontend/Dockerfile-dev data_copilot/frontend

build-frontend:
	docker build -t $(IMAGE_NAME_FRONTEND) -f dockerfiles/frontend/Dockerfile data_copilot/frontend

build-nginx:
	docker build -t $(IMAGE_NAME_NGINX) -f dockerfiles/nginx/Dockerfile .

build: build-backend build-celery-worker build-celery-flower build-frontend build-frontend-dev build-nginx

db-schema:
	eralchemy2 -i "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" -o database.png

client-sdk:
	set -a && source .dev.env && export ENVIRONMENT=TEST && set +a && python -m data_copilot.tools.create_openapi_json
	docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate -i /local/openapi.json --output /local/data_copilot/frontend/src/client -g typescript-axios
	rm openapi.json

check-client-sdk:
	make client-sdk
	git diff --exit-code frontend/src/client
	docker run --rm -v ${PWD}:/local --add-host=host.docker.internal:host-gateway openapitools/openapi-generator-cli generate -i http://host.docker.internal:8000/api/openapi.json --output /local/frontend/src/client -g typescript-axios

run: build-backend build-celery-worker build-celery-flower build-frontend build-nginx
	docker compose --env-file .dev.env -f docker-compose.yml up

run-dev: build-backend build-celery-worker build-celery-flower build-frontend-dev build-nginx
	docker compose --env-file .dev.env -f docker-compose-dev.yml up

install-frontend-dependencies: build-frontend-dev
	docker run --rm -v ${PWD}/frontend:/app -w /app $(IMAGE_NAME_FRONTEND)-dev npm install

reset-db: build-backend
	docker compose -f docker-compose-dev.yml --env-file .dev.env --profile reset_db run --rm reset-db

setup:
	python3 configure.py

launch-db:
	docker compose -f docker-compose-dev.yml --env-file .dev.env up database adminer