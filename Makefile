.PHONY: up down clean

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down --volumes --remove-orphans

docker-compose-clean:
	docker-compose down --volumes --remove-orphans
