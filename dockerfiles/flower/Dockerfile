FROM python:3.10

# Install Redis and RQ
WORKDIR /var/app
COPY dockerfiles/flower/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
ARG ENV
ENV ENV=${ENV}
ENV PYTHONPATH=/var/app/

# CMD ["python", "-m", "worker.worker"]
CMD ["celery", "flower"]
