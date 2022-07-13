# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -U setuptools wheel
RUN pip install -r requirements.txt
COPY . .

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0" ]