all: build up

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down -v

clean:
	docker container prune
	docker image prune