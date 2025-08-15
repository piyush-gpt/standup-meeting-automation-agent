# Core LangGraph agent logic
from db.models import get_users, create_standup_run
from slack.slack_client import send_dm_with_cache

async def collect_standups(workspace_id):
	"""
	Initiates a standup by creating a run and DMing every user.
	Returns run_id.
	"""
	run_id = create_standup_run(workspace_id, created_by="system")
	users = get_users(workspace_id)
	for u in users:
		try:
			await send_dm_with_cache(workspace_id, u["user_id"], "Good morning! Please reply with your standup: (Yesterday / Today / Blockers)")
		except Exception as e:
			print("Error DMing user:", u["user_id"], e)
	return run_id
