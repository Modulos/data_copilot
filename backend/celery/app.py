from celery import Celery

from backend.config import Config

CONFIG = Config()
execution_app = Celery("main", broker=CONFIG.REDIS_URL)
