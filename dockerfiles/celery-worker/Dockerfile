FROM python:3.10

# Create a non-root user and switch to it
RUN useradd -m celery_user
USER celery_user

# Install Redis and RQ
WORKDIR /home/celery_user/app
COPY dockerfiles/celery-worker/requirements.txt /tmp/requirements.txt
RUN pip install --user -r /tmp/requirements.txt
COPY --chown=celery_user:celery_user celery_app /home/celery_user/app/celery_app
COPY --chown=celery_user:celery_user db_models /home/celery_user/app/db_models
ARG ENV
ENV ENV=${ENV} \
    PYTHONPATH=/home/celery_user/app/ \
    PATH=/home/celery_user/.local/bin:$PATH

CMD ["celery", "-A", "celery_app.worker.execution_app", "worker", "--loglevel=info", "--concurrency=1"]
