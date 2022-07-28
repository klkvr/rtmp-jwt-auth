FROM python:3.9-buster

WORKDIR /app

RUN pip install pipenv
COPY src/Pipfile.lock /app
COPY src/Pipfile /app
RUN pipenv install --system --deploy --ignore-pipfile

COPY src/ /app

ENTRYPOINT uvicorn main:app --host 0.0.0.0 --forwarded-allow-ips="*"