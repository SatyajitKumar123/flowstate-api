from split_settings.tools import include
import os

ENV = os.environ.get("DJANGO_ENV", "development")

include(
    "base.py",
    f"environments/{ENV}.py",
)