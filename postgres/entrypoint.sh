#!/bin/bash

echo "Executing script..."

envsubst < init.template.sql > /docker-entrypoint-initdb.d/init.sql

echo "Finished executing script."