FROM python:3.11-alpine

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install gunicorn
RUN pip install -r requirements.txt
RUN pip install -r requirements-openmeteo.txt

RUN mkdir /var/log/gunicorn

EXPOSE 80/tcp

CMD ["gunicorn", "--bind", "0.0.0.0:80", "informer:app", "--access-logfile", "/var/log/gunicorn/informer.log", "--error-logfile", "/var/log/gunicorn/informer-error.log"]
