FROM python:3.13-slim
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update

ENV POETRY_HOME=/opt/poetry
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install -U pip setuptools
RUN $POETRY_HOME/bin/pip install poetry
RUN $POETRY_HOME/bin/poetry --version
RUN ln -sf $POETRY_HOME/bin/poetry /usr/local/bin/poetry

COPY ./src /backend/src
COPY migration /backend/migration
COPY alembic.ini /backend/
COPY pyproject.toml /backend/
ENV PYTHONPATH /backend/src
WORKDIR /backend

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

RUN chmod +x ./src/start.sh

EXPOSE 8000
