import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
PARENT_DIR = SCRIPT_DIR.parent

# Load .env and .secrets files with absolute paths FIRST
load_dotenv(PARENT_DIR / ".env")  # Loads from 05_src directory
load_dotenv(PARENT_DIR / ".secrets")  # Loads from 05_src directory

# --- Our Project Imports ---
# Import our system prompt
from assignment_chat.prompts import return_instructions

# Import our THREE service tools
from assignment_chat.tools_api import get_anime_info
from assignment_chat.tools_hotel import query_hotel_reviews
from assignment_chat.tools_simple import get_current_datetime
# --- End of Our Imports ---

# Initialize the chat model using ChatOpenAI directly
chat_agent = ChatOpenAI(model_name="gpt-4o-mini")

# --- THIS IS THE KEY CHANGE ---
# Give the agent OUR list of tools
tools = [get_anime_info, query_hotel_reviews, get_current_datetime]
# --- END OF KEY CHANGE ---


# Get the system instructions from our prompts file
instructions = return_instructions()


# This function is copied from the sample
# It calls the model and decides if a tool is needed
def call_model(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    response = chat_agent.bind_tools(tools).invoke( [SystemMessage(content=instructions)] + state["messages"])
    return {
        "messages": [response]
    }

# This function builds the graph
def get_graph():
    
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools)) # Use our tools list - name must be "tools"
    
    builder.add_edge(START, "call_model")
    
    builder.add_conditional_edges(
        "call_model",
        tools_condition, # This checks if the model wants to use a tool
    )
    builder.add_edge("tools", "call_model") # After using a tool, go back to the model
    
    return builder.compile()