import os

if os.environ.get("COMPUTE_BACKEND") == "sql":
    from celery_app.apps.sql_prompt_app import execution_app

elif os.environ.get("COMPUTE_BACKEND") == "pandasai":
    from celery_app.apps.pandasai_prompt_app import execution_app


__all__ = ["execution_app"]
