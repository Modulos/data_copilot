FROM python:3.10

# Create a non-root user and switch to it
RUN addgroup --gid 1000 celery_group && \
    adduser --uid 1000 --ingroup celery_group --home /home/celery_user --shell /bin/sh --disabled-password --gecos "" celery_user

USER celery_user

# Set up directories and permissions for our volumes
RUN mkdir -p /home/celery_user/app/shared-fs && \
    chown -R celery_user:celery_group /home/celery_user/app/shared-fs

# Install Redis and RQ
WORKDIR /home/celery_user/app
COPY dockerfiles/celery-worker/requirements.txt /tmp/requirements.txt
RUN pip install --user -r /tmp/requirements.txt
COPY --chown=celery_user:celery_user data_copilot/celery_app /home/celery_user/app/data_copilot/celery_app
COPY --chown=celery_user:celery_user data_copilot/db_models /home/celery_user/app/data_copilot/db_models
ARG ENV
ENV ENV=${ENV} \
    PYTHONPATH=/home/celery_user/app/ \
    PATH=/home/celery_user/.local/bin:$PATH

CMD ["celery", "-A", "celery_app.worker.execution_app", "worker", "--loglevel=info", "--concurrency=1"]
