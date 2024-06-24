PG_DATA	=	./data/postgres

all: build up

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	docker-compose down -v
	docker container prune --force
	docker image prune -a --force
	docker volume prune -a --force
	docker builder prune -a --force

fclean: down clean
	sudo rm -rf $(PG_DATA)

re: fclean all
