#!/bin/bash

set -e

envsubst < init.template.sql > /docker-entrypoint-initdb.d/init.sql

exec "$@"