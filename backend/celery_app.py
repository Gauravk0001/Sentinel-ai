"""
SentinelAI - Celery Application Configuration
Configures the Celery worker for background asynchronous tasks
(e.g. AI model retraining, alert generation, dashboard refresh).

Uses Redis as the broker and result backend.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from celery import Celery

from config import settings

# Celery app with Redis broker
celery_app = Celery(
    "sentinelai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,
    worker_max_tasks_per_child=10,  # Restart worker to avoid memory leaks
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)

# Ensure tasks module is imported so tasks are registered
import tasks  # noqa: E402,F401


if __name__ == "__main__":
    celery_app.start()
