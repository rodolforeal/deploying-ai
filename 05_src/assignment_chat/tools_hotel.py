import sys
from pathlib import Path

# Add parent directory to path to allow imports from utils
sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os
from langchain.tools import tool
from dotenv import load_dotenv

# --- Configuration ---

# Load environment variables (for OPENAI_API_KEY)
load_dotenv()  # Loads from .env in parent directory
load_dotenv(".secrets")  # Loads from .secrets in parent directory

# These MUST match the paths used in load_reviews.py
SCRIPT_DIR = Path(__file__).parent
DB_DIRECTORY = str(SCRIPT_DIR / "hotel_reviews_db")
COLLECTION_NAME = "hotel_reviews"

# Global variable to hold the collection
_collection = None

def _get_collection():
    """Lazy initialization of the ChromaDB collection."""
    global _collection
    if _collection is None:
        # 1. Initialize the embedding function - use ChromaDB's function
        embeddings_function = OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        # 2. Initialize a PERSISTENT client
        client = chromadb.PersistentClient(path=DB_DIRECTORY)
        
        # 3. Get the collection
        try:
            _collection = client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=embeddings_function
            )
            print("Successfully connected to ChromaDB collection 'hotel_reviews'.")
        except Exception as e:
            print(f"Error connecting to ChromaDB: {e}")
            _collection = None
    return _collection

# --- The Tool ---

@tool
def query_hotel_reviews(user_question: str) -> str:
    """
    Searches the hotel review database for information.
    Use this tool to answer any questions about hotel experiences,
    room quality, service, cleanliness, location, or specific hotel reviews.
    """
    collection = _get_collection()
    if collection is None:
        return "Sorry, I'm having trouble connecting to the review database."

    print(f"Querying hotel reviews for: '{user_question}'")

    try:
        # 1. Perform the query
        results = collection.query(
            query_texts=[user_question],
            n_results=3  # Get the top 3 most relevant chunks
        )
        
        # 2. Process and format the results
        output = "Here is what I found in the hotel reviews:\n\n"
        
        documents = results.get('documents', [])
        metadatas = results.get('metadatas', [])

        if not documents or not documents[0]:
            return "I searched the reviews, but couldn't find any specific information about that."

        for i in range(len(documents[0])):
            doc_text = documents[0][i]
            meta = metadatas[0][i]
            
            hotel_name = meta.get('hotel_name', 'Unknown Hotel')
            rating = meta.get('rating', 'N/A')
            
            output += f"--- Result {i+1} ---\n"
            output += f"Hotel: {hotel_name}\n"
            output += f"Rating: {rating}/10.0\n"
            output += f"Review Snippet: \"...{doc_text}...\"\n\n"
            
        return output

    except Exception as e:
        print(f"Error during query: {e}")
        return f"Sorry, an error occurred while searching the reviews."


# --- This is new testing code ---
if __name__ == "__main__":
    print("Testing the query_hotel_reviews() function:")
    print("=" * 30)

    # Make sure you have run load_reviews.py FIRST!
    collection = _get_collection()
    if collection:
        # Test 1: A general query
        query1 = "Was the service good?"
        print(f"Test 1: '{query1}'")
        print(query_hotel_reviews.invoke({"user_question": query1}))
        print("=" * 30)
        
        # Test 2: A specific query
        query2 = "How was the Hilton University of Houston?"
        print(f"Test 2: '{query2}'")
        print(query_hotel_reviews.invoke({"user_question": query2}))
        print("=" * 30)
    else:
        print("Could not run tests: Collection not loaded.")
        print("Did you run load_reviews.py first?")