import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0", "web"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

LLM_BACKEND = "ollama"
DEFAULT_FROM_EMAIL = "noreply@docflow.local"

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379:0")
CELERY_BROCKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
