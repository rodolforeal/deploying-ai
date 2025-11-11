import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🔄 Loading The Concierge Chat App...")
print("⏳ Please wait while libraries are initialized (this may take 30-60 seconds)...")

import gradio as gr
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

print("📦 Loading agent configuration...")

# --- KEY CHANGE ---
# Import the graph from OUR main.py
from assignment_chat.main import get_graph
# --- END OF KEY CHANGE ---


# Load secrets
load_dotenv()  # Loads from parent directory
load_dotenv('.secrets')  # Loads from parent directory

print("🤖 Initializing agent...")
# Initialize our agent
llm_graph = get_graph()

print("✅ Agent ready!")
print("🚀 Starting Gradio interface...")
print()

def assignment_chat_func(message: str, history: list[dict]) -> str:
    """
    This is the main function that Gradio calls on every user message.
    """
    print(f"History: {history}")
    
    # Convert Gradio's history format to LangChain's message format
    langchain_messages = []
    for msg in history:
        if msg['role'] == 'user':
            langchain_messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            langchain_messages.append(AIMessage(content=msg['content']))
            
    # Add the new user message
    langchain_messages.append(HumanMessage(content=message))

    # Define the "state" for the graph
    # We don't need 'llm_calls' from the sample, this is simpler
    state = {
        "messages": langchain_messages,
    }

    # Invoke the agent
    response_state = llm_graph.invoke(state)
    
    # Return the agent's LAST message as the response
    last_message = response_state['messages'][-1]
    return last_message.content

# Create the Gradio Chat Interface
chat_ui = gr.ChatInterface(
    fn=assignment_chat_func,
    title="Assignment 2 Chatbot (The Concierge)",
    type="messages"
)

# Run the app
if __name__ == "__main__":
    print("=" * 60)
    print("🎉 The Concierge Chat App is ready!")
    print("=" * 60)
    chat_ui.launch()