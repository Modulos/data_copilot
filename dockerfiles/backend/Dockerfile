FROM python:3.10-slim

# Create a non-root user and switch to it
RUN useradd -m fastapi_user
USER fastapi_user

# Install the application
WORKDIR /home/fastapi_user/app
COPY --chown=fastapi_user:fastapi_user dockerfiles/backend/requirements.txt /home/fastapi_user/app/requirements.txt
RUN pip install --user -r /home/fastapi_user/app/requirements.txt
COPY --chown=fastapi_user:fastapi_user backend /home/fastapi_user/app/backend
COPY --chown=fastapi_user:fastapi_user alembic.ini /home/fastapi_user/app/alembic.ini
COPY --chown=fastapi_user:fastapi_user db_migrations /home/fastapi_user/app/db_migrations
COPY --chown=fastapi_user:fastapi_user db_models /home/fastapi_user/app/db_models
COPY --chown=fastapi_user:fastapi_user storage_handler /home/fastapi_user/app/storage_handler
ARG ENV
ENV ENV=${ENV} \
    PYTHONPATH=/home/fastapi_user/app/ \
    PATH=/home/fastapi_user/.local/bin:$PATH
EXPOSE 80
CMD ["uvicorn", "backend.main:app", "--host=0.0.0.0", "--port=80", "--log-level=debug"]
