FROM python:3.9-slim

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install poetry
ENV POETRY_VIRTUALENVS_CREATE false
RUN poetry install --no-dev

WORKDIR ./src
COPY config ./config
COPY db ./db
COPY email_sender ./email_sender
COPY security ./security
COPY utils ./utils

CMD poetry run python email_sender/main.py
