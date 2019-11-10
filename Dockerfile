# dockerfile for server django app

# base img
FROM python:3.6

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
RUN mkdir /TeamPizza
WORKDIR /TeamPizza

# install dependecies
COPY requirements /TeamPizza/
RUN pip install -r requirements

# copy project repository
COPY . /TeamPizza/

# prepare django db
RUN chmod +x migrations.sh

# "Running django server"
ENTRYPOINT /TeamPizza/migrations.sh
ENTRYPOINT python3 /TeamPizza/manage.py runserver 0.0.0.0:8000

