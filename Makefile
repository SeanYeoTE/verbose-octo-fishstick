

build:
	docker compose -f docker-compose.yml build

up:
	docker compose -f docker-compose.yml up

down:
	docker compose -f docker-compose.yml down

clean:
	docker compose -f docker-compose.yml down --volumes --remove-orphans --rmi all

re: clean build up

