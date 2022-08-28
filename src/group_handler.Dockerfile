FROM python:3.9-slim

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install poetry
ENV POETRY_VIRTUALENVS_CREATE false
RUN poetry install --no-dev

WORKDIR ./src
COPY config ./config
COPY db ./db
COPY group_handler ./group_handler
COPY security ./security
COPY utils ./utils

CMD poetry run python group_handler/main.py
