# LangGraph workflow definition
from typing import TypedDict, Sequence
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
import asyncio
import time
from db.models import get_channel_preference
# Import our agents
from agents.standup_agent import collect_standups
from agents.summarizer_agent import summarize_standups

# Global app instance for reuse
_standup_app = None

# State definition
class StandupState(TypedDict):
    workspace_id: str
    run_id: str
    messages: Sequence[str]
    current_step: str
    completed: bool
    channel_id: str  # Channel to post summary to

# Node functions
async def collect_standups_node(state: StandupState) -> StandupState:
    
    # Call the standup collection function
    run_id = await collect_standups(state['workspace_id'])
    
    # Update state
    updated_state = {
        **state,
        "run_id": run_id,
        "current_step": "waiting_for_responses",
        "messages": [*state["messages"], f"Standup collection initiated. Run ID: {run_id}. Workflow paused for 5 minutes..."]
    }
    
    
    return updated_state

async def summarize_standups_node(state: StandupState) -> StandupState:
    value=interrupt({
        "content": f"Standup collection completed for run {state['run_id']}",
        "type": "standup_collection_complete",
        "run_id": state['run_id'],
        "workspace_id": state["workspace_id"]
    })
    
    try:
        # Pass the channel_id to the summarizer
        summary = await summarize_standups(state['workspace_id'], state['run_id'], state.get('channel_id'))
        
        return {
            **state,
            "current_step": "completed",
            "completed": True,
            "messages": [*state["messages"], f"Standup summary completed and posted to channel:\n{summary}"]
        }
    except Exception as e:
        error_msg = f"Error summarizing standups: {str(e)}"
        print(error_msg)
        return {
            **state,
            "current_step": "error",
            "completed": True,
            "messages": [*state["messages"], error_msg]
        }

# Create the graph
def create_standup_graph():
    """Create the standup workflow graph with interrupt capability"""
    
    # Create the graph
    workflow = StateGraph(StandupState)
    
    # Add nodes
    workflow.add_node("collect_standups", collect_standups_node)
    workflow.add_node("summarize_standups", summarize_standups_node)
    
    # Add edges
    workflow.add_edge("collect_standups", "summarize_standups")
    workflow.add_edge("summarize_standups", END)
    
    # Set entry point
    workflow.set_entry_point("collect_standups")
    
    # Compile with persistence
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

def get_standup_app():
    """Get or create the standup app instance"""
    global _standup_app
    if _standup_app is None:
        _standup_app = create_standup_graph()
    return _standup_app

# Helper function to start a standup workflow
def start_standup_workflow(workspace_id: str, channel_id: str = None, thread_id: str = None):
    """Start a new standup workflow for a workspace"""
    
    # Create initial state
    initial_state = StandupState(
        workspace_id=workspace_id,
        run_id="",
        messages=[],
        current_step="collecting",
        completed=False,
        channel_id=channel_id or ""
    )
    
    # Create the graph
    app = create_standup_graph()
    
    # Start the workflow
    if thread_id:
        # Resume existing thread
        config = {"configurable": {"thread_id": thread_id}}
        result = app.invoke(initial_state, config)
    else:
        # Start new thread - need to provide configurable keys for checkpointer
        new_thread_id = f"standup_{workspace_id}_{int(time.time())}"
        config = {"configurable": {"thread_id": new_thread_id}}
        result = app.invoke(initial_state, config)
        # Add thread_id to result for external use
        result["thread_id"] = new_thread_id
    
    return result


# Function to resume a paused workflow using Command
def resume_standup_workflow(thread_id: str, app: StateGraph):
    """Resume a paused standup workflow after the wait period"""
    
    try:
        # Use Command to resume the workflow
        command = Command(resume={})
        config = {"configurable": {"thread_id": thread_id}}
        result = app.invoke(command, config=config)
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Async versions (these are the main functions to use)
async def start_standup_workflow_async(workspace_id: str, channel_id: str = None, thread_id: str = None, app: StateGraph = None):
    """Async version of the standup workflow"""
    # Create initial state
    initial_state = StandupState(
        workspace_id=workspace_id,
        run_id="",
        messages=[],
        current_step="collecting",
        completed=False,
        channel_id=channel_id or ""
    )
    
    # Use provided app or get global instance
    app = app or get_standup_app()

    
    # Start the workflow
    result = {}
    if thread_id:
        # Resume existing thread
        config = {"configurable": {"thread_id": thread_id}}
        result = await app.ainvoke(initial_state, config=config)
        result["thread_id"] = thread_id
    else:
        # Start new thread - need to provide configurable keys for checkpointer
        print("Starting new thread")
        new_thread_id = f"standup_{workspace_id}_{int(time.time())}"
        config = {"configurable": {"thread_id": new_thread_id}}
        result = await app.ainvoke(initial_state, config=config)
        # Add thread_id to result for external use
        result["thread_id"] = new_thread_id
    print(f"Result: {result}")
    return result


async def resume_standup_workflow_async(thread_id: str, app: StateGraph = None):
    """Async version to resume a paused standup workflow using Command"""
    print(f"Resuming workflow for thread: {thread_id}")
    app = app or get_standup_app()
    
    try:
        # Use Command to resume the workflow
        command = Command(resume={"resume": True})
        config = {"configurable": {"thread_id": thread_id}}
        print(f"Config: {config}")
        result = await app.ainvoke(command, config=config)
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Function to check workflow status
async def check_workflow_status(thread_id: str, app: StateGraph = None):
    """Check the current status of a workflow thread"""
    app = app or get_standup_app()
    
    try:
        config = {"configurable": {"thread_id": thread_id}}
        return {"status": "checking", "thread_id": thread_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def start_standup_with_timer_async(workspace_id: str, channel_id: str = None, app: StateGraph = None):
    """Start a standup workflow and automatically resume after 5 minutes"""
    print(f"🚀 Starting async standup workflow for workspace: {workspace_id}")
    if channel_id:
        print(f"📢 Summary will be posted to channel: {channel_id}")
    
    app = app or get_standup_app()
    
    # Start the workflow
    result = await start_standup_workflow_async(workspace_id, channel_id=channel_id, app=app)
    
    if "thread_id" in result:
        thread_id = result["thread_id"]
        print(f"✅ Workflow started with thread ID: {thread_id}")
        print("⏸️  Workflow paused after standup collection. Waiting 5 minutes...")
        
        # Wait for 5 minutes
        await asyncio.sleep(90)  # 5 minutes = 300 seconds
        
        print(f"⏰ 5 minutes elapsed. Resuming workflow with thread ID: {thread_id}")
        try:
            resume_result = await resume_standup_workflow_async(thread_id, app=app)
            print(f"✅ Workflow resumed: {resume_result}")
        except Exception as e:
            print(f"❌ Error resuming workflow: {e}")
        
        return thread_id
    else:
        print("❌ Failed to start workflow - no thread_id in result")
        return None

# HTTP endpoint functions for scheduler integration
async def start_standup_endpoint(workspace_id: str, channel_id: str = None):
    """HTTP endpoint function to start a standup workflow"""
    try:
        print(f"🚀 Starting standup for workspace: {workspace_id}")
        
        # Get channel preference if not provided
        if not channel_id:
            channel_pref = get_channel_preference(workspace_id)
            if channel_pref:
                channel_id = channel_pref["channel_id"]
                print(f"Using stored channel: {channel_pref['channel_name']} ({channel_id})")
            else:
                print("Warning: No channel selected for this workspace")
        
        # Start the workflow using global app instance
        result = await start_standup_workflow_async(workspace_id, channel_id=channel_id, app=get_standup_app())
        
        if "thread_id" in result:
            print(f"✅ Standup started successfully. Thread ID: {result['thread_id']}")
            return {
                "success": True,
                "thread_id": result["thread_id"],
                "workspace_id": workspace_id,
                "channel_id": channel_id
            }
        else:
            print("❌ Failed to start standup workflow")
            return {
                "success": False,
                "error": "Failed to start workflow"
            }
            
    except Exception as e:
        print(f"❌ Error starting standup: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def resume_standup_endpoint(thread_id: str):
    """HTTP endpoint function to resume a standup workflow"""
    try:
        print(f"⏰ Resuming standup workflow for thread: {thread_id}")
        
        result = await resume_standup_workflow_async(thread_id, app=get_standup_app())
        
        if "status" in result and result["status"] == "error":
            print(f"❌ Error resuming workflow: {result['error']}")
            return {
                "success": False,
                "error": result["error"]
            }
        else:
            print(f"✅ Workflow resumed successfully")
            return {
                "success": True,
                "thread_id": thread_id,
                "result": result
            }
            
    except Exception as e:
        print(f"❌ Error resuming standup: {e}")
        return {
            "success": False,
            "error": str(e)
        }
