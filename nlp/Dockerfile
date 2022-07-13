FROM python:3.8.10-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
# RUN apt-get -y install gcc
# RUN apt-get -y install libc6-dev
RUN apt-get -y install build-essential

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools wheel
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .