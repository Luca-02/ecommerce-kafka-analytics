up:
	docker-compose up -d

down:
	docker-compose down --volumes --remove-orphans

clean:
	docker-compose down --volumes --remove-orphans
	docker system prune --volumes -f
