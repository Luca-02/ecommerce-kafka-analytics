init:
	cd analytics-service && python -m venv .venv && call .venv/Scripts/activate && pip install -r requirements.dev.txt
	cd event-simulator-service && python -m venv .venv && call .venv/Scripts/activate && pip install -r requirements.dev.txt
	bash ./scripts/generate.sh

firebase-start:
	cd firebase && firebase emulators:start

compose-dev-up:
	docker-compose -f docker-compose-dev.yml up -d
compose-dev-down:
	docker-compose -f docker-compose-dev.yml down --volumes

compose-up:
	docker-compose -f docker-compose.yml up -d --build
compose-down:
	docker-compose -f docker-compose.yml down --volumes

attacker-up:
	docker-compose -f docker-compose-attacker.yml up -d --build
attacker-down:
	docker-compose -f docker-compose-attacker.yml down --volumes

kafka-up:
	docker-compose -f docker-compose-kafka.yml up -d --build
kafka-down:
	docker-compose -f docker-compose-kafka.yml down --volumes

services-up:
	docker-compose -f docker-compose-services.yml up -d --build
services-down:
	docker-compose -f docker-compose-services.yml down --volumes

all-down:
	docker-compose -f docker-compose-dev.yml -f docker-compose.yml -f docker-compose-attacker.yml down --volumes

docker-clean:
	docker system prune --volumes -f

docker-build:
	docker build -t ecommerce-kafka-analytics/analytics-service:latest -f analytics-service/Dockerfile .
	docker build -t ecommerce-kafka-analytics/event-simulator-service:latest -f event-simulator-service/Dockerfile .
