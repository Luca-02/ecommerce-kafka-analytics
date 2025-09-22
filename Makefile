init:
	cd analytics-service && python -m venv .venv && call .venv/Scripts/activate && pip install -r requirements.dev.txt
	cd event-simulator-service && python -m venv .venv && call .venv/Scripts/activate && pip install -r requirements.dev.txt

firebase-start:
	cd firebase && firebase emulators:start

compose-pull:
	docker-compose pull

compose-up:
	docker-compose up -d --build

compose-down:
	docker-compose down --volumes --remove-orphans

compose-down-up:
	docker-compose down --volumes --remove-orphans
	docker-compose up -d --build

docker-clean:
	docker system prune --volumes -f
