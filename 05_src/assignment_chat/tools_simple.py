import datetime
from langchain.tools import tool

@tool
def get_current_datetime() -> str:
    """
    Returns the current date and time in a human-readable format.
    Use this tool when the user asks for the current time or date.
    """
    # Get the current time
    now = datetime.datetime.now()
    
    # Format it into a nice string
    formatted_time = now.strftime("%A, %B %d, %Y at %I:%M %p")
    
    return f"The current date and time is: {formatted_time}"


# --- This is new testing code ---
if __name__ == "__main__":
    print("Testing the get_current_datetime() function:")
    
    # Call your function using invoke() since it's decorated with @tool
    current_time = get_current_datetime.invoke({})
    
    # Print the result
    print(current_time)
