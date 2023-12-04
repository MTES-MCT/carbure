# This image will serve as the base image for the GitLab CI jobs
FROM ubuntu:latest

ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT 1

RUN apt-get update -y

RUN apt-get install -y \
  curl \
  git \
  python3.10 \
  python3-dev \
  python3-pip \
  mysql-client \
  libmysqlclient-dev

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

COPY front/package.json front/package.json
COPY front/package-lock.json front/package-lock.json
RUN (cd front; npm clean-install)

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pip3 install pipenv
RUN pipenv install --dev --deploy --system
