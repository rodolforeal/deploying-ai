import requests
from langchain.tools import tool

@tool
def get_anime_info(anime_title: str) -> str:
    """
    Searches for an anime on MyAnimeList and returns a
    human-readable summary of its details, including
    score, episode count, status, and synopsis.
    """
    print(f"Searching for '{anime_title}'...")

    # 1. Define the API endpoint
    params = {"q": anime_title, "limit": 1}

    try:
        # 2. Make the API call
        response = requests.get("https://api.jikan.moe/v4/anime", params=params, timeout=10)

        # 3. Check for a successful response (HTTP status code 200)
        if response.status_code == 200:
            # 4. Parse the JSON data
            data = response.json()

            # Check if the 'data' list has any results
            if data.get('data'):
                # Get the first anime from the results list
                anime_data = data['data'][0]

                # 5. Transform the data (THE KEY REQUIREMENT)
                
                # --- Safely get data ---
                title = anime_data.get('title', 'N/A')
                score = anime_data.get('score', 'N/A')
                episodes = anime_data.get('episodes', 'N/A')
                status = anime_data.get('status', 'N/A')
                synopsis = anime_data.get('synopsis', 'No summary available.')

                # --- Build the final string ---
                output = (
                    f"Here's what I found for '{title}':\n"
                    f"It's rated {score}/10 and has {episodes} episodes.\n"
                    f"Current status: {status}\n\n"
                    f"Summary:\n{synopsis}"
                )
                
                return output
            
            else:
                return f"Sorry, I couldn't find any anime with the title '{anime_title}'."

        elif response.status_code == 429:
            return "Sorry, the API is rate limiting requests. Please try again shortly."
        else:
            # Handle API errors
            return f"Sorry, I had trouble connecting to the API. (Status Code: {response.status_code})"

    except requests.exceptions.Timeout:
        return "Sorry, the request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        # Handle network errors (e.g., no internet)
        return f"Sorry, a network error occurred: {e}"

# --- This is new testing code ---
if __name__ == "__main__":
    print("Testing the get_anime_info() function:")
    
    # Test with a popular anime
    anime_name_1 = "Attack on Titan"
    print(get_anime_info.invoke({"anime_title": anime_name_1}))
    
    print("-" * 20)
    
    # Test with a movie
    anime_name_2 = "Spirited Away"
    print(get_anime_info.invoke({"anime_title": anime_name_2}))