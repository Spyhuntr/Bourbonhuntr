FROM ubuntu:latest 

ARG WORKING_DIR=/app
WORKDIR ${WORKING_DIR}
COPY ${GITHUB_WORKSPACE} /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHON UNBUFFERED 1

RUN apt update && apt upgrade -y \
    python3-pip && apt-get install -y python3.6 wget unzip curl && \
    pip3 install -r requirements.txt && \
    apt autoremove -y

EXPOSE 8050

CMD gunicorn index:server \
--bind 0.0.0.0:8050 \
--timeout 120 \
--workers 3