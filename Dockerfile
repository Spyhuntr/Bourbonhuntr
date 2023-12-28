FROM ubuntu:latest 

WORKDIR /app
COPY . /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHON UNBUFFERED 1

RUN apt-get update && apt-get install --no-install-recommends -y \
  python3-pip \
  python3-dev \
  libpq-dev \
  wget \
  curl \
  && pip3 install -r requirements.txt

EXPOSE 8050

ENTRYPOINT [ "gunicorn", "--config", "gunicorn_config.py", "app:server" ]