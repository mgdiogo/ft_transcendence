FROM debian:stable-slim

WORKDIR /app

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y nodejs npm

COPY ./tools/server.mjs .

RUN npm cache clean --force && \
    npm init -y && \
    npm install fastify

CMD [ "node", "server.mjs" ]