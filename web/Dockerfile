# Use the official Ubuntu image as the base image
FROM ubuntu:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/venv
ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PATH="/venv/bin:$PATH"

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

# Install uv
RUN pip install uv

# Copy Python dependency metadata
COPY pyproject.toml uv.lock /app/

# Install dependencies using uv
RUN uv sync --frozen --no-install-project

# Copy the rest of your application code
COPY web web
COPY scripts scripts
COPY bin bin

# Set the default command to execute the application
CMD ["sh", "./web/entrypoint.sh"]
