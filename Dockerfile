# dockerfile for server django app

# base img
FROM python:3.6

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
RUN mkdir /TeamPizza
WORKDIR /TeamPizza
RUN mkdir /ssl
# WORKDIR /ssl
RUN mkdir /ssl/key
RUN mkdir /ssl/cert

# install dependecies
COPY requirements /TeamPizza/
RUN pip install -r requirements

# copy project repository
COPY ./TeamPizza/* /TeamPizza/
COPY ./ssl/key/* /ssl/key
COPY ./ssl/cert/* /ssl/cert

# prepare django db
RUN chmod +x /TeamPizza/migrations.sh

# "Running django server"
#ENTRYPOINT python3 /TeamPizza/manage.py migrate --noinput
#ENTRYPOINT python3 /TeamPizza/manage.py runserver 0.0.0.0:8000

