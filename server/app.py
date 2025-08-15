from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from dotenv import load_dotenv
from db.models import get_workspace_by_id, get_all_workspaces, update_channel_preference, get_channel_preference
from slack_sdk.web.client import WebClient

load_dotenv()

from slack.oauth import install_url, oauth_callback
from slack.event_handler import handle_event, verify_slack_request
from graph import start_standup_endpoint, resume_standup_endpoint
import asyncio

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://standup-frontend:3000"], supports_credentials=True)

@app.route("/slack/install", methods=["GET"])
def install():
    return redirect(install_url())

@app.route("/slack/oauth/callback", methods=["GET"])
def oauth_cb():
    code = request.args.get("code")
    return oauth_callback(code)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    # verify signature
    if not verify_slack_request(request):
        return jsonify({"error": "verification_failed"}), 403

    payload = request.json
    # url_verification challenge
    if payload.get("type") == "url_verification":
        return jsonify({"challenge": payload.get("challenge")})

    # handle regular events
    return handle_event(payload)

@app.route("/api/channels/<workspace_id>", methods=["GET"])
def get_channels(workspace_id):
    """Get available channels for a workspace"""
    workspace = get_workspace_by_id(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    
    bot_token = workspace.get("bot_token")
    if not bot_token:
        return jsonify({"error": "bot token not found"}), 400
    
    try:
        # Use Slack SDK instead of direct HTTP requests
        client = WebClient(token=bot_token)
        response = client.conversations_list(types="public_channel,private_channel")
        
        if response.get("ok"):
            channels = response.get("channels", [])
            # Filter out channels the bot can't post to
            available_channels = [
                {
                    "id": channel["id"],
                    "name": channel["name"],
                    "is_private": channel.get("is_private", False)
                }
                for channel in channels
                if not channel.get("is_archived", False)
            ]
            return jsonify({"channels": available_channels})
        else:
            return jsonify({"error": response.get("error", "Unknown error")}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/channels/<workspace_id>", methods=["POST"])
def set_channel(workspace_id):
    """Set the selected channel for a workspace"""
    workspace = get_workspace_by_id(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    
    data = request.get_json()
    channel_id = data.get("channel_id")
    channel_name = data.get("channel_name")
    standup_time = data.get("standup_time")
    timezone = data.get("timezone")
    
    if not channel_id:
        return jsonify({"error": "channel_id is required"}), 400
    
    try:
        update_channel_preference(workspace_id, channel_id, channel_name or channel_id, standup_time, timezone)
        return jsonify({"success": True, "message": "Channel and schedule updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/workspace/<workspace_id>/channel", methods=["GET"])
def get_workspace_channel(workspace_id):
    """Get the selected channel for a workspace"""
    workspace = get_workspace_by_id(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    
    channel_pref = get_channel_preference(workspace_id)
    if channel_pref:
        selected_channel = {
            "id": channel_pref["channel_id"],
            "name": channel_pref["channel_name"]
        }
    else:
        selected_channel = None
    
    return jsonify({"selected_channel": selected_channel})


# List installed workspaces
@app.route("/workspaces", methods=["GET"])
def list_workspaces():
    return jsonify(list(get_all_workspaces()))

# Get single workspace
@app.route("/workspaces/<workspace_id>", methods=["GET"])
def get_workspace(workspace_id):
    workspace = get_workspace_by_id(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    
    return jsonify({
        "workspace_id": workspace["workspace_id"],
        "workspace_name": workspace["workspace_name"]
    })

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok"})

# LangGraph endpoints for scheduler integration
@app.route("/start", methods=["POST"])
def start_standup():
    """Start a standup workflow - called by scheduler"""
    try:
        data = request.get_json()
        workspace_id = data.get("workspace_id")
        channel_id = data.get("channel_id")
        
        if not workspace_id:
            return jsonify({"error": "workspace_id is required"}), 400
        
        # Run the async function
        result = asyncio.run(start_standup_endpoint(workspace_id, channel_id))
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resume", methods=["POST"])
def resume_standup():
    """Resume a standup workflow - called by scheduler"""
    try:
        data = request.get_json()
        thread_id = data.get("thread_id")
        
        if not thread_id:
            return jsonify({"error": "thread_id is required"}), 400
        
        # Run the async function
        result = asyncio.run(resume_standup_endpoint(thread_id))
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
