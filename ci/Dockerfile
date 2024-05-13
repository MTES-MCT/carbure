# This image will serve as the base image for the GitLab CI jobs
FROM ubuntu:latest

ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT 1

RUN apt-get update -y && apt-get install -y \
  curl \
  git \
  python3 \
  python3-dev \
  python3-venv \
  python3-pip \
  build-essential \
  pkg-config \
  default-libmysqlclient-dev \
  mysql-client

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

COPY front/package.json front/package.json
COPY front/package-lock.json front/package-lock.json
RUN (cd front; npm clean-install)

# Create a virtual environment and activate it
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Pipenv using pip
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock /app/

# Install dependencies using Pipenv
RUN pipenv install --dev --deploy
