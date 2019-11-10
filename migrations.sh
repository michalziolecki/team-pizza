#!/bin/sh
echo "creating migrations"
python3 /TeamPizza/manage.py makemigrations --noinput
python3 /TeamPizza/manage.py migrate --noinput
exit $?

