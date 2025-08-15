from celery import Celery
from celery.schedules import crontab
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://standup-redis:6379/0")

celery = Celery(
    "standup",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.timezone = "UTC"

celery.conf.beat_scheduler = "redbeat.RedBeatScheduler"
celery.conf.redbeat_redis_url = REDIS_URL

celery.conf.redbeat_lock_key = None  

import tasks

celery.conf.beat_schedule = {
    "refresh-every-2-mins": {
        "task": "tasks.refresh_schedules",
        "schedule": crontab(minute="*/2"),
    }
}
