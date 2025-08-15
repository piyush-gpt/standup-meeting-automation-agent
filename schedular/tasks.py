from celery_app import celery
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry
from pymongo import MongoClient
from datetime import datetime, timezone
import pytz
import requests
import os

LANGGRAPH_SERVICE_URL = os.getenv("LANGGRAPH_SERVICE_URL")
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["standup"]

@celery.task
def refresh_schedules():
    print("🔄 Refreshing schedules from MongoDB...")
    schedules = db["channel_preferences"].find()

    schedule_count = 0
    for sched in schedules:
        workspace_id = sched["workspace_id"]
        channel_id = sched["channel_id"] if sched["channel_id"] else sched["channel_name"]
        time_str = sched["standup_time"]
        tz_str = sched["timezone"]
        if not time_str or not tz_str:
            continue

        local_tz = pytz.timezone(tz_str)
        now_utc = datetime.now(timezone.utc)
        local_time = datetime.strptime(time_str, "%H:%M").replace(
            year=now_utc.year,
            month=now_utc.month,
            day=now_utc.day
        )
        local_dt = local_tz.localize(local_time)
        utc_dt = local_dt.astimezone(pytz.UTC)

        hour_utc = utc_dt.hour
        minute_utc = utc_dt.minute

        print(f"📅 Scheduling standup for {workspace_id} at {hour_utc}:{minute_utc} UTC")

        # Create/update schedule entry in Redis
        entry = RedBeatSchedulerEntry(
            name=f"standup_{workspace_id}",
            task="tasks.start_standup_task",
            schedule=crontab(hour=hour_utc, minute=minute_utc),
            args=(workspace_id, channel_id),
            app=celery
        )
        entry.save()
        schedule_count += 1

    print(f"✅ Total schedules loaded: {schedule_count}")

@celery.task
def start_standup_task(workspace_id, channel_id=None):
    print(f"🚀 Starting standup task for workspace: {workspace_id}")
    payload = {"workspace_id": workspace_id, "channel_id": channel_id}
    r = requests.post(f"{LANGGRAPH_SERVICE_URL}/start", json=payload)

    if r.ok:
        thread_id = r.json().get("thread_id")
        if thread_id:
            resume_standup_task.apply_async(args=[thread_id], countdown=120)
        return r.json()
    else:
        return {"error": r.text}

@celery.task
def resume_standup_task(thread_id):
    r = requests.post(f"{LANGGRAPH_SERVICE_URL}/resume", json={"thread_id": thread_id})
    return r.json()
