FROM ubuntu:latest 

ARG WORKING_DIR=/app
WORKDIR ${WORKING_DIR}
COPY ${GITHUB_WORKSPACE} /app

EXPOSE 8050

RUN apt update && apt upgrade -y \
    python3-pip && apt-get install -y python3.6 wget unzip curl && \
    pip3 install -r requirements.txt && \
    apt autoremove -y

CMD ["python3", "index.py"]