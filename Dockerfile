FROM ubuntu:latest 

WORKDIR /app
COPY . /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHON UNBUFFERED 1

RUN apt-get update \
    && apt-get upgrade -y python3-pip \
    && apt-get install -y python3.8 wget curl \
    && pip3 install -r requirements.txt \
    && apt autoremove -y

EXPOSE 8050

CMD gunicorn index:server \
--bind 0.0.0.0:8050 \
--timeout 120 \
--workers 3