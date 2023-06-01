FROM python:3.10-slim

RUN apt update
RUN apt install -y curl

# Create a non-root user and switch to it
RUN addgroup --gid 1000 fastapi_group && \
    adduser --uid 1000 --ingroup fastapi_group --home /home/fastapi_user --shell /bin/sh --disabled-password --gecos "" fastapi_user

USER fastapi_user

# Set up directories and permissions for our volumes
RUN mkdir -p /home/fastapi_user/app/shared-fs && \
    chown -R fastapi_user:fastapi_group /home/fastapi_user/app/shared-fs

# Install the application
WORKDIR /home/fastapi_user/app
COPY --chown=fastapi_user:fastapi_user dockerfiles/backend/requirements.txt /home/fastapi_user/app/requirements.txt
RUN pip install --user -r /home/fastapi_user/app/requirements.txt
COPY --chown=fastapi_user:fastapi_user data_copilot/backend /home/fastapi_user/app/data_copilot/backend
COPY --chown=fastapi_user:fastapi_user alembic.ini /home/fastapi_user/app/alembic.ini
COPY --chown=fastapi_user:fastapi_user data_copilot/db_migrations /home/fastapi_user/app/data_copilot/db_migrations
COPY --chown=fastapi_user:fastapi_user data_copilot/db_models /home/fastapi_user/app/data_copilot/db_models
COPY --chown=fastapi_user:fastapi_user data_copilot/storage_handler /home/fastapi_user/app/data_copilot/storage_handler
ARG ENV
ENV ENV=${ENV} \
    PYTHONPATH=/home/fastapi_user/app/ \
    PATH=/home/fastapi_user/.local/bin:$PATH
EXPOSE 80
CMD ["uvicorn", "data_copilot.backend.main:app", "--host=0.0.0.0", "--port=80", "--log-level=debug"]
