FROM python:3.12.16

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/venv
ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PATH="/venv/bin:$PATH"

# Run updates and install necessary system packages
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y \
  build-essential \
  pkg-config \
  default-libmysqlclient-dev

# Set up working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy Python dependency metadata
COPY pyproject.toml uv.lock /app/

# Install dependencies using uv
RUN uv sync --frozen --no-install-project

# Copy the rest of your application code
COPY web web
COPY scripts scripts
COPY backups backups
COPY bin bin

# Set the default command to execute the application
CMD ["sh", "./web/entrypoint.sh"]
