FROM python:3.11-alpine

WORKDIR /app
COPY . /app

# Copy the necessary uv files
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Setup uv and install the packages
RUN uv sync --group openmeteo
RUN uv add gunicorn 

# Create the log directory
RUN mkdir /var/log/gunicorn && chmod 777 /var/log/gunicorn

EXPOSE 8181/tcp

# Run gunicorn with 6 workers
CMD ["uv", "run", "--with", "gunicorn", "gunicorn", "--bind", "0.0.0.0:8181", "informer:app", "--threads", "1", "--workers", "6", "--access-logfile", "/var/log/gunicorn/informer.log", "--error-logfile", "/var/log/gunicorn/informer-error.log"]
