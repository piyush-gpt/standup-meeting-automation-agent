from .mongo import db
from datetime import datetime
from bson.objectid import ObjectId

workspaces_col = db["workspaces"]
users_col = db["users"]
runs_col = db["standup_runs"]
responses_col = db["standup_responses"]
channel_preferences_col = db["channel_preferences"]

# Workspaces
def save_workspace(workspace_id, workspace_name, bot_token, installer=None):
    workspaces_col.update_one(
        {"workspace_id": workspace_id},
        {"$set": {
            "workspace_name": workspace_name,
            "bot_token": bot_token,
            "installer": installer,
            "installed_at": datetime.utcnow()
        }},
        upsert=True
    )

def get_workspace_by_id(workspace_id):
    return workspaces_col.find_one({"workspace_id": workspace_id})

def get_all_workspaces():
    return list(workspaces_col.find({}, {"_id": 0, "workspace_id": 1, "workspace_name": 1}))

# Channel preferences
def save_channel_preference(workspace_id, channel_id, channel_name):
    """Save the selected channel for a workspace"""
    channel_preferences_col.update_one(
        {"workspace_id": workspace_id},
        {"$set": {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )

def get_channel_preference(workspace_id):
    """Get the selected channel for a workspace"""
    return channel_preferences_col.find_one({"workspace_id": workspace_id})

def update_channel_preference(workspace_id, channel_id, channel_name, standup_time=None, timezone=None):
    """Update the selected channel and schedule for a workspace"""
    update_data = {
        "channel_id": channel_id,
        "channel_name": channel_name,
        "updated_at": datetime.utcnow()
    }
    
    if standup_time is not None:
        update_data["standup_time"] = standup_time
    if timezone is not None:
        update_data["timezone"] = timezone
    
    channel_preferences_col.update_one(
        {"workspace_id": workspace_id},
        {"$set": update_data},
        upsert=True
    )

# Users
def save_user(workspace_id, user_id, real_name=None, dm_channel_id=None):
    users_col.update_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {"$set": {
            "real_name": real_name,
            "dm_channel_id": dm_channel_id,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )

def get_users(workspace_id):
    return list(users_col.find({"workspace_id": workspace_id}))

def get_user(workspace_id, user_id):
    return users_col.find_one({"workspace_id": workspace_id, "user_id": user_id})

def update_user_dm(workspace_id, user_id, dm_channel_id):
    users_col.update_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {"$set": {"dm_channel_id": dm_channel_id, "updated_at": datetime.utcnow()}}
    )

# Standup runs & responses
def create_standup_run(workspace_id, created_by="system"):
    res = runs_col.insert_one({
        "workspace_id": workspace_id,
        "created_by": created_by,
        "created_at": datetime.utcnow(),
        "status": "open"
    })
    return str(res.inserted_id)

def close_standup_run(run_id):
    runs_col.update_one({"_id": ObjectId(run_id)}, {"$set": {"status": "closed", "closed_at": datetime.utcnow()}})

def save_response(workspace_id, run_id, user_id, text, raw_event=None, ts=None):
    responses_col.insert_one({
        "workspace_id": workspace_id,
        "run_id": run_id,
        "user_id": user_id,
        "text": text,
        "raw_event": raw_event,
        "ts": ts,
        "created_at": datetime.utcnow()
    })

def get_responses_for_run(workspace_id, run_id):
    return list(responses_col.find({"workspace_id": workspace_id, "run_id": run_id}))

def clear_responses_for_workspace(workspace_id):
    responses_col.delete_many({"workspace_id": workspace_id})
