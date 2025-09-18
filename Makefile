compose-up:
	docker-compose up -d

compose-down:
	docker-compose down --volumes --remove-orphans

docker-clean:
	docker system prune --volumes -f

firebase-start:
	cd analytics-service/firebase && \
	firebase emulators:start --import=./export --export-on-exit