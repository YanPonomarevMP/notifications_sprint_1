FROM python:3.9-slim

EXPOSE 5000/tcp

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

CMD gunicorn main:app --bind 0.0.0.0:5000 -k uvicorn.workers.UvicornWorker
