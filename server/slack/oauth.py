# Slack OAuth flow for multi-workspace
import os, requests, asyncio
from flask import jsonify, redirect
from dotenv import load_dotenv
from db.models import save_workspace
from slack.slack_client import make_client_and_sync_users

load_dotenv()

CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
BASE_URL = os.getenv("BASE_URL") 
REDIRECT_URI = f"{BASE_URL}/slack/oauth/callback"

def install_url():
    scopes = [
        "assistant:write",
        "im:write",
        "users:read",
        "channels:read",
        "groups:read",
        "chat:write",
        "im:history",
        "incoming-webhook"
    ]
    scope_str = ",".join(scopes)
    return f"https://slack.com/oauth/v2/authorize?client_id={CLIENT_ID}&scope={scope_str}&redirect_uri={REDIRECT_URI}"

def oauth_callback(code):
    # Exchange code for tokens
    url = "https://slack.com/api/oauth.v2.access"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    r = requests.post(url, data=data)
    resp = r.json()
    if not resp.get("ok"):
        return jsonify({"error": resp}), 400

    bot_token = resp.get("access_token")
    team = resp.get("team", {})
    workspace_id = team.get("id") or resp.get("team_id")
    workspace_name = team.get("name") or resp.get("team", {}).get("name")

    save_workspace(workspace_id, workspace_name, bot_token, installer=resp.get("authed_user", {}).get("id"))

    try:
        asyncio.run(make_client_and_sync_users(workspace_id, bot_token))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(make_client_and_sync_users(workspace_id, bot_token))

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    setup_url = f"{frontend_url}/setup?workspace_id={workspace_id}"
    return redirect(setup_url)
