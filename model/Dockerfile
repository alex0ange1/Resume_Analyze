FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install grpcio grpcio-tools

COPY src/ ./src/
COPY data/ ./data/

ENV PYTHONPATH ./src

RUN chmod +x ./src/start.sh
