from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]

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
