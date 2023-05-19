import os

if os.environ.get("COMPUTE_BACKEND") == "sql":
    from celery_app.apps.sql_prompt_app import execution_app

elif os.environ.get("COMPUTE_BACKEND") == "getting_started":
    from celery_app.apps.getting_started_example import execution_app

else:
    raise Exception("No compute backend specified")

__all__ = ["execution_app"]
