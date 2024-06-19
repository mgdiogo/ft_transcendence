FROM postgres

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gettext

EXPOSE 5432

COPY entrypoint.sh /docker-entrypoint-initdb.d/entrypoint.sh
COPY init.template.sql /init.template.sql

RUN chmod +x /docker-entrypoint-initdb.d/entrypoint.sh \
    && sed -i 's/\r//' /docker-entrypoint-initdb.d/entrypoint.sh \
    && chown postgres:postgres /docker-entrypoint-initdb.d/entrypoint.sh \
    && chown -R postgres:postgres /docker-entrypoint-initdb.d/

CMD [ "postgres" ]
