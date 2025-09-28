FROM python:3.11-alpine

WORKDIR /app
COPY . /app

# Copy the necessary uv files
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Setup uv and install the packages
RUN uv init --bare
RUN uv add gunicorn -r requirements.txt -r requirements-openmeteo.txt
RUN rm requirements.txt requirements-openmeteo.txt

# Create the log directory
RUN mkdir /var/log/gunicorn && chmod 777 /var/log/gunicorn

EXPOSE 8181/tcp

CMD ["uv", "run", "--with", "gunicorn", "gunicorn", "--bind", "0.0.0.0:8181", "informer:app", "--access-logfile", "/var/log/gunicorn/informer.log", "--error-logfile", "/var/log/gunicorn/informer-error.log"]
