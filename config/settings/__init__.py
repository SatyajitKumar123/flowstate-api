from split_settings.tools import include
import os

from config.celery import app as celery_app

__all__=("celery_app",)

ENV = os.environ.get("DJANGO_ENV", "development")

include(
    "base.py",
    f"environments/{ENV}.py",
)