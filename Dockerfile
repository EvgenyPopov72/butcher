FROM python:3.10-alpine

RUN apk update && \
    apk upgrade && \
    apk add --no-cache ffmpeg

COPY . /opt/butcher
WORKDIR /opt/butcher

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]