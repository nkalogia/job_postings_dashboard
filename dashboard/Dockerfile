FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update
RUN apt-get -y install build-essential

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -U setuptools wheel
RUN pip install -r requirements.txt

COPY . .

# CMD [ "gunicorn", "--workers=4", "-b 0.0.0.0:8050", "index:server" ]