init:
	cd analytics-service && python -m venv .venv && call .venv/Scripts/activate && pip install -r requirements.dev.txt
	cd event-simulator-service && python -m venv .venv && call .venv/Scripts/activate && pip install -r requirements.dev.txt

firebase-start:
	cd firebase && firebase emulators:start

kafka-up:
	docker-compose -f docker-compose-kafka.yml up -d

kafka-down:
	docker-compose -f docker-compose-kafka.yml down --volumes

ui-up:
	docker-compose -f docker-compose-ui.yml up -d

ui-down:
	docker-compose -f docker-compose-ui.yml down --volumes

services-up:
	docker-compose -f docker-compose-services.yml up -d --build

services-down:
	docker-compose -f docker-compose-services.yml down --volumes

docker-clean:
	docker system prune --volumes -f
