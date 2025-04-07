FROM debian:stable-slim

WORKDIR /app

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y nodejs npm

COPY ./tools/app.mjs .

RUN npm cache clean --force && \
    npm init -y && \
    npm install fastify && \
    npm install tailwindcss @tailwindcss/cli

CMD [ "node", "app.mjs" ]