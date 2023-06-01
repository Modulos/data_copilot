from celery import Celery

from data_copilot.backend.config import Config

CONFIG = Config()
execution_app = Celery("main", broker=CONFIG.CELERY_BROKER_URL)
