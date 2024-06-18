FROM postgres

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gettext

RUN mkdir -p /var/lib/postgresql/data \
    && chown -R postgres:postgres /var/lib/postgresql/data

EXPOSE 5432

COPY entrypoint.sh /entrypoint.sh
COPY init.template.sql /init.template.sql

RUN chmod +x /entrypoint.sh \
    && chown postgres:postgres /entrypoint.sh \
    && chown -R postgres:postgres /docker-entrypoint-initdb.d/

USER postgres

ENTRYPOINT ["/entrypoint.sh"]

CMD ["postgres"]
