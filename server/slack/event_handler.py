# Slack event processing
import os, hmac, hashlib, time
from flask import make_response
from db.models import save_response
from dotenv import load_dotenv
from datetime import datetime, timedelta
from db.models import runs_col

load_dotenv()
SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

def verify_slack_request(req):
    timestamp = req.headers.get("X-Slack-Request-Timestamp")
    if not timestamp:
        return False
    # protect against replay attacks
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False
    sig_basestring = f"v0:{timestamp}:{req.get_data(as_text=True)}"
    my_sig = "v0=" + hmac.new(
        SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    slack_sig = req.headers.get("X-Slack-Signature")
    return hmac.compare_digest(my_sig, slack_sig)

def get_open_standup_run(workspace_id):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    run = runs_col.find_one({
        "workspace_id": workspace_id,
        "status": "open",
        "created_at": {"$gte": today_start, "$lt": today_end}
    })

    if run:
        return str(run["_id"])
    else:
        return None

def handle_event(payload):
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        if event.get("type") == "message" and event.get("channel_type") == "im" and not event.get("bot_id"):
            workspace_id = payload.get("team_id")
            user_id = event.get("user")
            text = event.get("text")
            ts = event.get("ts")

            run_id = get_open_standup_run(workspace_id)
            if run_id:
                save_response(workspace_id, run_id, user_id, text, raw_event=event, ts=ts)
            else:
                pass
    return make_response("", 200)
