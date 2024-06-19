all: build up

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down -v

clean:
	docker container prune --force
	docker image prune -a --force
	docker volume prune -a --force
	docker builder prune -a --force

fclean: down clean

re: fclean all
