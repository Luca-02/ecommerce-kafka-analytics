init:
	cd analytics-service && python -m venv .venv && call .venv/Scripts/activate && pip install -r requirements.dev.txt
	cd event-simulator-service && python -m venv .venv && call .venv/Scripts/activate && pip install -r requirements.dev.txt

compose-pull:
	docker-compose pull

compose-up:
	docker-compose up -d --build

compose-down:
	docker-compose down --volumes --remove-orphans

docker-clean:
	docker system prune --volumes -f

firebase-start:
	cd firebase && \
	firebase emulators:start
