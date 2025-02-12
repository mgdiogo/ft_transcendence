FROM debian:stable-slim

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y curl && \
    apt-get clean

COPY ./config/script.sh ./script.sh
RUN chmod +x script.sh

COPY ./tools/package.json ./package.json
COPY ./tools/server.js ./server.js

ENTRYPOINT [ "./script.sh" ]

CMD [ "node", "server" ]