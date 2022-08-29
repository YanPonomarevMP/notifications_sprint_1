FROM python:3.9.13-slim

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install poetry
ENV POETRY_VIRTUALENVS_CREATE false
RUN poetry install --no-dev

WORKDIR ./src
COPY config ./config
COPY db ./db
COPY email_formatter ./email_formatter
COPY security ./security
COPY utils ./utils

CMD poetry run python email_formatter/main.py
