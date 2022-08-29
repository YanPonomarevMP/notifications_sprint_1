FROM python:3.9.13-slim

EXPOSE 8000/tcp

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install poetry
ENV POETRY_VIRTUALENVS_CREATE false
RUN poetry install --no-dev

WORKDIR ./src
COPY config ./config
COPY db ./db
COPY notifier_api ./notifier_api
COPY security ./security
COPY utils ./utils

CMD poetry run python notifier_api/main.py
