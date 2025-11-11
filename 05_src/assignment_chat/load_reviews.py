import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os
from dotenv import load_dotenv

# --- Configuration ---

# Load environment variables (for OPENAI_API_KEY)
load_dotenv()  # Loads from .env in parent directory
load_dotenv(".secrets")  # Loads from .secrets in parent directory

# 1. Define paths - use absolute paths based on script location
SCRIPT_DIR = Path(__file__).parent
CSV_FILE_PATH = SCRIPT_DIR / "hotel_reviews.csv"  # CSV is in the same directory as script
DB_DIRECTORY = SCRIPT_DIR / "hotel_reviews_db"  # This folder will be created in script directory
COLLECTION_NAME = "hotel_reviews"

# 2. Initialize components - use ChromaDB's embedding function
embeddings_function = OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# Simple text splitter function
def split_text(text, chunk_size=1000, chunk_overlap=100):
    """Split text into chunks with overlap."""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
        
        # Avoid infinite loop if chunk_overlap >= chunk_size
        if chunk_overlap >= chunk_size:
            start = end
            
    return chunks

client = chromadb.PersistentClient(path=DB_DIRECTORY)

# 3. Create or get the collection
try:
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embeddings_function
    )
    print(f"Collection '{COLLECTION_NAME}' created.")
except Exception as e:
    # Collection might already exist
    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embeddings_function
        )
        print(f"Collection '{COLLECTION_NAME}' already exists. Re-using.")
    except Exception as e2:
        print(f"Error with collection: {e2}")
        collection = None


# --- Main Loading Function ---
def load_data_from_csv():
    """
    Loads data from the CSV, processes it, and adds it to ChromaDB.
    """
    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
        print("Please check the path and try again.")
        return

    # Filter for relevant columns and drop rows with no review text
    df = df[['review_id', 'review_text', 'hotel_name', 'overall_ratings']].dropna(subset=['review_text'])

    # --- Prepare data for ChromaDB ---
    all_documents = []
    all_metadatas = []
    all_ids = []

    print(f"Processing {len(df)} reviews...")

    for index, row in df.iterrows():
        # 1. Split the review text into smaller chunks
        chunks = split_text(row['review_text'], chunk_size=1000, chunk_overlap=100)
        
        for i, chunk in enumerate(chunks):
            # 2. Create documents (the text to be embedded)
            all_documents.append(chunk)

            # 3. Create metadatas (info about the chunk)
            all_metadatas.append({
                "hotel_name": row['hotel_name'],
                "rating": float(row['overall_ratings']),
                "source_review_id": str(row['review_id'])
            })
            
            # 4. Create unique IDs
            all_ids.append(f"{row['review_id']}_{i}")

    # --- Add to ChromaDB in batches ---
    print(f"Adding {len(all_documents)} document chunks to ChromaDB...")
    
    # Add to collection in batches of 1000 to avoid overwhelming the system
    batch_size = 1000
    for i in range(0, len(all_documents), batch_size):
        batch_docs = all_documents[i:i + batch_size]
        batch_metas = all_metadatas[i:i + batch_size]
        batch_ids = all_ids[i:i + batch_size]
        
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        print(f"Added batch {i // batch_size + 1}")

    print("\n--- Success! ---")
    print(f"Vector database created at: ./{DB_DIRECTORY}")
    print(f"Total reviews processed: {len(df)}")
    print(f"Total text chunks added: {len(all_documents)}")


# --- Run the script ---
if __name__ == "__main__":
    load_data_from_csv()