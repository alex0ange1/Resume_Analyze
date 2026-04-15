ARG PYTHON_VERSION=3.13.12

# builder
FROM python:${PYTHON_VERSION}-slim AS builder

ENV POETRY_VERSION=2.2.1
ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-cache-dir \
    poetry==${POETRY_VERSION} \
    poetry-plugin-export

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    poetry export -o /tmp/requirements.txt


# main
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,from=builder,source=/tmp/requirements.txt,target=/tmp/requirements.txt \
    python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./src ./src
COPY migration ./migration
COPY alembic.ini ./
ENV PYTHONPATH ./src

RUN chmod +x ./src/start.sh
