FROM ubuntu:latest

RUN apt-get update -y

RUN apt-get install -y \
  git \
  python3.10 \
  python3-dev \
  python3-pip \
  mysql-client \
  libmysqlclient-dev

ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT 1

WORKDIR /app

COPY Pipfile ./
COPY Pipfile.lock ./
RUN pip3 install pipenv
RUN pipenv install --system --deploy

COPY web web
COPY scripts scripts

CMD [ "bash", "./web/entrypoint.sh" ]