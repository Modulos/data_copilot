import os

if os.environ.get("COMPUTE_BACKEND") == "sql":
    from data_copilot.celery_app.apps.sql_prompt_app import execution_app

elif os.environ.get("COMPUTE_BACKEND") == "getting_started":
    from data_copilot.celery_app.apps.getting_started_example import execution_app

elif os.environ.get("COMPUTE_BACKEND") == "langchain":
    from data_copilot.celery_app.apps.langchain_prompt_app import execution_app

else:
    raise Exception("No compute backend specified")

__all__ = ["execution_app"]
