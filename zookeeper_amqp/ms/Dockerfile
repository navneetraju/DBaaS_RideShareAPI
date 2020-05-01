FROM python:3.7-slim-stretch
RUN apt-get update
RUN apt-get install -y mysql-server
RUN mkdir -p /code
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
COPY . /code
WORKDIR /code
