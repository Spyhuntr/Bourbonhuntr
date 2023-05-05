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

ENTRYPOINT [ "gunicorn", "--config", "gunicorn_config.py", "app:server" ]