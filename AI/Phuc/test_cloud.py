"""
ChromaDB Cloud Test File
========================
This file uses ChromaDB Cloud to store and query embeddings.

SETUP INSTRUCTIONS:
1. Install chromadb: pip install chromadb
2. Login to Chroma Cloud: chroma login
3. Create a database: chroma db create lotara-tourism
4. Connect to database: chroma db connect lotara-tourism --env-file
   (This creates a .env file with CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE)
5. Run this script: python test_cloud.py
"""

import chromadb
import os
import json
import time
import re
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file (created by chroma db connect)
load_dotenv()


def load_api_key(path="api_key.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: file {path} not found")
        exit()


# GenAI client for embeddings
genai_client = genai.Client(api_key=load_api_key())

# -----------------------------
# Initialize ChromaDB Client
# -----------------------------
# Try Cloud first, fallback to local PersistentClient
USE_CLOUD = True  # Cloud is now configured!

if USE_CLOUD:
    try:
        chroma_api_key = os.getenv("CHROMA_API_KEY")
        chroma_tenant = os.getenv("CHROMA_TENANT")
        chroma_database = os.getenv("CHROMA_DATABASE")
        
        if chroma_api_key and chroma_tenant and chroma_database:
            print(f"Connecting to Chroma Cloud...")
            print(f"  Tenant: {chroma_tenant}")
            print(f"  Database: {chroma_database}")
            
            chroma_client = chromadb.CloudClient(
                tenant=chroma_tenant,
                database=chroma_database,
                api_key=chroma_api_key
            )
            print("Connected to Chroma Cloud successfully!\n")
        else:
            raise ValueError("Missing CHROMA_API_KEY, CHROMA_TENANT, or CHROMA_DATABASE in .env file")

    except Exception as e:
        print(f"Failed to connect to Chroma Cloud: {e}")
        print("\nTo use Chroma Cloud, run these commands first:")
        print("  1. chroma login")
        print("  2. chroma db create lotara-tourism")
        print("  3. chroma db connect lotara-tourism --env-file")
        print("\nFalling back to local storage...\n")
        USE_CLOUD = False

if not USE_CLOUD:
    # Use local PersistentClient (works without any cloud setup)
    persist_dir = os.path.join(os.path.dirname(__file__), "chroma_cloud_data")
    chroma_client = chromadb.PersistentClient(path=persist_dir)
    print(f"Using local ChromaDB storage at: {persist_dir}\n")

# Create or get collection
collection = chroma_client.get_or_create_collection(name="Lotara")
print(f"Collection 'Lotara' ready. Current count: {collection.count()}")

# -----------------------------
# Load JSON data
# -----------------------------
json_path = os.path.join(os.path.dirname(__file__), "VN_tourism_EN_v3.json")
try:
    with open(json_path, "r", encoding="utf-8") as f:
        locations = json.load(f)
    print(f"Loaded {len(locations)} locations from JSON.")
except FileNotFoundError:
    print("Error: file VN_tourism_EN_v3.json not found")
    exit()

# Build index lookup for quick access by Index
locations_by_index = {item.get("Index"): item for item in locations}


# -----------------------------
# Convert complex JSON to text (same as Embedding.py)
# -----------------------------
def location_to_text(item):
    sections = []

    # 1. Core identity
    sections.append(
        f"Location name: {item.get('Location name', '')}. "
        f"Province or city: {item.get('Location', '')}. "
        f"Description: {item.get('Description', '')}. "
        f"Keywords: {item.get('Keywords', '')}. "
        f"Overall rating: {item.get('Rating', '')} out of 5."
    )

    # 2. Destinations: Places & Food (with attributes)
    destination_texts = []
    for dest in item.get("Destinations", []):
        place = dest.get("place", {})
        cuisine = dest.get("cuisine", {})

        if place:
            destination_texts.append(
                f"Attraction: {place.get('name', '')}, "
                f"best time to visit: {place.get('time', 'anytime')}, "
                f"budget level: {place.get('budget', 'unknown')}, "
                f"average duration: {place.get('average_timespan', 'unknown')}."
            )

        if cuisine:
            destination_texts.append(
                f"Local food spot: {cuisine.get('name', '')}, "
                f"budget level: {cuisine.get('budget', 'unknown')}, "
                f"average dining time: {cuisine.get('average_timespan', 'unknown')}."
            )

    if destination_texts:
        sections.append("Experiences and nearby spots: " + " ".join(destination_texts))

    # 3. Hotels (with cost & review sentiment)
    hotel_texts = []
    for hotel in item.get("Hotels", []):
        hotel_texts.append(
            f"Hotel: {hotel.get('name', '')}, "
            f"cost category: {hotel.get('cost', 'unknown')}, "
            f"review quality: {hotel.get('reviews', 'unknown')}."
        )

    if hotel_texts:
        sections.append("Accommodation options: " + " ".join(hotel_texts))

    # 4. Activities (VERY IMPORTANT for intent matching)
    activities = item.get("Activities", [])
    if activities:
        sections.append(
            "Popular activities include: " + ", ".join(activities) + "."
        )

    # 5. Final combined text
    full_text = " ".join(sections)
    return full_text


# Embed using the same GenAI call pattern as in Embedding.py
def get_embedding(text, model="text-embedding-004"):
    result = genai_client.models.embed_content(model=model, contents=[text])
    vec = result.embeddings[0].values
    return vec


def get_embeddings_batch(texts, model="text-embedding-004"):
    """Embed multiple texts at once for efficiency"""
    result = genai_client.models.embed_content(model=model, contents=texts)
    return [e.values for e in result.embeddings]


# -----------------------------
# Check if data already exists in Cloud
# -----------------------------
def upload_data_to_cloud():
    """Upload location data to Chroma Cloud if not already present"""
    current_count = collection.count()
    
    if current_count >= len(locations):
        print(f"Data already exists in cloud ({current_count} items). Skipping upload.")
        return
    
    print(f"Uploading {len(locations)} locations to Chroma Cloud...")
    
    # Batch processing for efficiency
    BATCH_SIZE = 25
    total_batches = (len(locations) - 1) // BATCH_SIZE + 1

    for batch_idx in range(total_batches):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(locations))
        batch_locations = locations[start_idx:end_idx]
        
        print(f"Processing batch {batch_idx + 1} / {total_batches} (items {start_idx + 1} to {end_idx})...")
        
        # Prepare batch data
        batch_documents = []
        batch_metadatas = []
        batch_ids = []
        
        for item in batch_locations:
            doc_text = location_to_text(item)
            batch_documents.append(doc_text)
            
            # Store useful metadata for filtering/display
            metadata = {
                "index": item.get("Index", 0),
                "location_name": item.get("Location name", ""),
                "province": item.get("Location", ""),
                "rating": float(item.get("Rating", 0)),
                "keywords": item.get("Keywords", ""),
                "image": item.get("Image", ""),
            }
            batch_metadatas.append(metadata)
            batch_ids.append(str(item.get("Index", start_idx)))
        
        # Get embeddings for the batch
        batch_embeddings = get_embeddings_batch(batch_documents)
        
        # Upsert to ChromaDB Cloud
        collection.upsert(
            documents=batch_documents,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids,
        )
        
        # Pause briefly to avoid rate limits
        time.sleep(2)

    print(f"\nSuccess! Stored {len(locations)} locations in Chroma Cloud.")
    print(f"Collection count: {collection.count()}")


# --------------------------------------------------
# Retrieval using ChromaDB Cloud
# --------------------------------------------------
def retrieve_top_k(query, k=10):
    """Retrieve top k locations from ChromaDB Cloud based on query"""
    query_embedding = get_embedding(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["metadatas", "distances"]
    )
    
    # Get full location data from the original JSON using index
    retrieved_locations = []
    for meta in results["metadatas"][0]:
        idx = meta.get("index")
        if idx in locations_by_index:
            retrieved_locations.append(locations_by_index[idx])
    
    return retrieved_locations


# --------------------------------------------------
# JSON extractor (CRITICAL FIX)
# --------------------------------------------------
def extract_json(text: str):
    if not text or not text.strip():
        raise ValueError("Empty response from LLM")

    # Remove markdown fences if present
    cleaned = re.sub(r"```json|```", "", text).strip()

    # Try to find and parse the entire JSON array
    # Find the first '[' and last ']' to get the full array
    start_idx = cleaned.find('[')
    end_idx = cleaned.rfind(']')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = cleaned[start_idx:end_idx + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to fix common issues
            pass
    
    # Fallback: try parsing the whole cleaned text
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    raise ValueError("No valid JSON found in LLM output")


# --------------------------------------------------
# Generation (STRICT JSON SELECTOR)
# --------------------------------------------------
def recommend_locations(user_query, top_k=5):
    retrieved = retrieve_top_k(user_query, k=10)

    # IMPORTANT: pass RAW JSON, not flattened text
    context_json = json.dumps(retrieved, ensure_ascii=False, indent=2)

    prompt = f"""
You are a strict JSON selector.

Return ONLY a valid JSON array.
Do NOT explain.
Do NOT use markdown.
Do NOT include any text outside JSON.

Task:
Select the best {top_k} locations that best match the user profile.

Selection priorities:
1. Match with travel style, pace, and activity level
2. Cultural relevance
3. Budget compatibility
4. Overall rating

User profile:
{user_query}

Available locations (JSON array):
{context_json}

Output format:
[
  {{
    "Location name": string,
    "Location": string,
    "Description": string,
    "Rating": number,
    "Image": string,
    "Keywords": string,
    "Destinations": array,
    "Hotels": array,
    "Activities": array
  }}
]

Return ONLY JSON.
"""

    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw_text = response.text

    try:
        return extract_json(raw_text)
    except Exception as e:
        print("\n----- RAW LLM OUTPUT (DEBUG) -----")
        print(raw_text)
        print("---------------------------------\n")
        raise e


# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    # Upload data to cloud if needed
    upload_data_to_cloud()
    
    user_input = "Give me some place near the Hoan Kiem lake"

    print(f"\nAnalyzing your request: '{user_input}'...\n")

    try:
        results = recommend_locations(user_input, top_k=5)

        print("=" * 50)
        print("LOTARA RECOMMENDATIONS (FROM CHROMA CLOUD)")
        print("=" * 50)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"ERROR: {e}")
