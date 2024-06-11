#!/bin/sh

echo "Executing script..."

python manage.py migrate

exec "$@"
