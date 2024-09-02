# Use the official Ubuntu image as the base image
FROM ubuntu:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIPENV_VENV_IN_PROJECT 1

# Run updates and install necessary system packages
RUN apt-get update -y && apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-dev \
  git \
  build-essential \
  pkg-config \
  default-libmysqlclient-dev \
  mysql-client

# Set up working directory
WORKDIR /app

# Create a virtual environment and activate it
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Pipenv using pip
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock /app/

# Install dependencies using Pipenv
RUN pipenv install --dev --deploy

# Copy the rest of your application code
COPY web web
COPY scripts scripts
COPY bin bin

# Set the default command to execute the application
CMD ["pipenv", "run", "sh", "./web/entrypoint.sh"]