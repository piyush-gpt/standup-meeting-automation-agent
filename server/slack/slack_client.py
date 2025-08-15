# Slack API wrappers
from slack_sdk.web.async_client import AsyncWebClient
from db.models import save_user, update_user_dm, get_users, get_workspace_by_id, get_user, get_channel_preference, create_standup_run
from dotenv import load_dotenv

load_dotenv()

# Helper: create client from workspace token saved in DB
async def get_client_for_workspace(workspace_id):
	ws = get_workspace_by_id(workspace_id)
	if not ws:
		raise Exception("Workspace not found")
	token = ws.get("bot_token")
	return AsyncWebClient(token=token)

# On install: sync users and store dm ids
async def make_client_and_sync_users(workspace_id, bot_token):
	client = AsyncWebClient(token=bot_token)
	cursor = None
	while True:
		resp = await client.users_list(cursor=cursor)
		for m in resp.get("members", []):
			uid = m.get("id")
			# Skip Slackbot and any bot/deleted users
			if not uid or uid == "USLACKBOT" or m.get("is_bot") or m.get("deleted"):
				continue
			real_name = m.get("profile", {}).get("real_name") or m.get("name")
			# open dm (returns existing DM if already opened)
			dm = await client.conversations_open(users=[uid])
			dm_id = dm["channel"]["id"]
			save_user(workspace_id, uid, real_name, dm_id)
		cursor = resp.get("response_metadata", {}).get("next_cursor")
		if not cursor:
			break

# Send DM using cached dm_channel_id; open & update if missing
async def send_dm_with_cache(workspace_id, user_id, text):
	# Skip Slackbot explicitly
	if user_id == "USLACKBOT":
		return
	client = await get_client_for_workspace(workspace_id)
	u = get_user(workspace_id, user_id)
	dm = u.get("dm_channel_id") if u else None
	try:
		if not dm:
			res = await client.conversations_open(users=[user_id])
			dm = res["channel"]["id"]
			if u:
				update_user_dm(workspace_id, user_id, dm)
			else:
				save_user(workspace_id, user_id, None, dm)
		await client.chat_postMessage(channel=dm, text=text)
	except Exception as e:
		# try to re-open and retry once
		res = await client.conversations_open(users=[user_id])
		dm = res["channel"]["id"]
		update_user_dm(workspace_id, user_id, dm)
		await client.chat_postMessage(channel=dm, text=text)

# Post a message to a channel (channel id or name)
async def post_message_to_channel(workspace_id, channel, text):
	print(f"Posting message to channel: {channel}")
	client = await get_client_for_workspace(workspace_id)
	await client.chat_postMessage(channel=channel, text=text)

# Start a standup: create run, DM all users
async def start_standup_for_workspace(workspace_id, created_by="system", channel_id=None):
	run_id = create_standup_run(workspace_id, created_by=created_by)
	
	# If no channel_id provided, try to get it from the workspace settings
	if not channel_id:
		channel_pref = get_channel_preference(workspace_id)
		if channel_pref:
			channel_id = channel_pref["channel_id"]
			print(f"Using stored channel: {channel_pref['channel_name']} ({channel_id})")
		else:
			print("Warning: No channel selected for this workspace. Summary will not be posted.")
	
	users = get_users(workspace_id)
	for u in users:
		uid = u.get("user_id")
		# Skip Slackbot explicitly
		if uid == "USLACKBOT":
			continue
		try:
			await send_dm_with_cache(workspace_id, uid, "Good morning! Standup time — please reply with: Yesterday / Today / Blockers")
		except Exception as e:
			print("send dm error", e)
	return run_id
