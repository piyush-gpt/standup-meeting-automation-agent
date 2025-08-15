# Summarization part
from db.models import get_responses_for_run, close_standup_run
from slack.slack_client import post_message_to_channel
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def summarize_standups(workspace_id, run_id, channel_id=None):
	"""
	Summarize standups and optionally post to a channel
	
	Args:
		workspace_id: The Slack workspace ID
		run_id: The standup run ID
		channel_id: Optional channel ID to post summary to (e.g., "#general" or "C1234567890")
	"""
	print(f"Summarizing standups for run {run_id}")
	responses = get_responses_for_run(workspace_id, run_id)
	if not responses:
		print("No responses collected.")
		summary = "No responses collected."
	else:
		assembled = "\n".join([f"- <@{r['user_id']}>: {r['text']}" for r in responses])

		if OPENAI_API_KEY:
			try:
				llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
				print(f"Using OpenAI API")
				prompt = f"Summarize these standup updates grouped by person and extract blockers:\n\n{assembled}\n\nReturn a short summary and then a Blockers section."
				# If you switch to the async OpenAI client, update this await accordingly
				resp = llm.invoke([{"role": "user", "content": prompt}])
				summary = resp.content
			except Exception as e:
				print("OpenAI error:", e)
				summary = fallback_summary(assembled)
		else:
			print("No OpenAI API key found, using fallback summary")
			summary = fallback_summary(assembled)

	# close the run
	close_standup_run(run_id)
	
	# Post summary to channel if specified
	if channel_id:
		print(f"Posting summary to channel: {channel_id}")
		try:
			await post_message_to_channel(workspace_id, channel_id, summary)
			print(f"✅ Summary posted to channel: {channel_id}")
		except Exception as e:
			print(f"❌ Error posting summary to channel: {e}")
	
	return summary

def fallback_summary(assembled_text):
	# Very small heuristic summarizer: group lines and detect 'block' keywords
	lines = assembled_text.splitlines()
	persons = {}
	blockers = []
	for line in lines:
		if line.startswith("- <@"):
			try:
				user_part, text = line.split(">: ", 1)
				user = user_part[3:]
			except ValueError:
				continue
			persons.setdefault(user, []).append(text)
			lower = text.lower()
			if "block" in lower or "blocked" in lower or "stuck" in lower or "waiting" in lower:
				blockers.append(f"{user}: {text}")
	summary_lines = ["**Standup Summary**"]
	for u, texts in persons.items():
		summary_lines.append(f"<@{u}> — {' | '.join(texts)}")
	if blockers:
		summary_lines.append("\n**Blockers**")
		for b in blockers:
			summary_lines.append(f"- {b}")
	return "\n".join(summary_lines)
