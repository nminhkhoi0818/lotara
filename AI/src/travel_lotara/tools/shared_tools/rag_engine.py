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


def load_api_key():
    """
    Load Google GenAI API key from environment variables.
    
    Looks for GOOGLE_API_KEY or GOOGLE_GENAI_API_KEY in .env file.
    
    Returns:
        str: API key
        
    Raises:
        ValueError: If API key not found in environment
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Google GenAI API key not found. "
            "Please set GOOGLE_API_KEY or GOOGLE_GENAI_API_KEY in your .env file"
        )
    
    return api_key


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
# Embedding function for queries only
# -----------------------------
def get_embedding(text, model="text-embedding-004"):
    """Generate embedding for query text (not for uploading data)"""
    result = genai_client.models.embed_content(model=model, contents=[text])
    vec = result.embeddings[0].values
    return vec


# --------------------------------------------------
# --------------------------------------------------
# Extract clean description from document text
# --------------------------------------------------
def extract_description(text: str) -> str:
    """Extract just the description part from document text."""
    import re
    # Pattern: "Description: <text>. Keywords:"
    pattern = r'Description:\s*([^.]+(?:\.[^K]+)*?)\s*\.\s*Keywords:'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    # Fallback: return first sentence after "Description:"
    pattern2 = r'Description:\s*([^.]+)'
    match2 = re.search(pattern2, text)
    if match2:
        return match2.group(1).strip()
    return ""


# --------------------------------------------------
# Parse structured data from document text
# --------------------------------------------------
def parse_document_text(text: str) -> dict:
    """
    Parse Destinations, Hotels, and Activities from document text.
    
    Text format:
    "...Attraction: Name, best time: morning, budget level: medium, average duration: 4h. 
    Local food spot: Name, budget level: high, average dining time: 2h. 
    Hotel: Name, cost category: high, review quality: excellent.
    Popular activities include: Activity1, Activity2, ..."
    """
    parsed = {
        "Destinations": [],
        "Hotels": [],
        "Activities": []
    }
    
    # Parse Attractions and Cuisine (Destinations)
    import re
    
    # Find all attractions
    attraction_pattern = r'Attraction:\s*([^,]+),\s*best time to visit:\s*([^,]+),\s*budget level:\s*([^,]+),\s*average duration:\s*([^.]+)'
    attractions = re.findall(attraction_pattern, text)
    
    # Find all food spots
    food_pattern = r'Local food spot:\s*([^,]+),\s*budget level:\s*([^,]+),\s*average dining time:\s*([^.]+)'
    foods = re.findall(food_pattern, text)
    
    # Combine attractions and foods into Destinations
    for idx in range(max(len(attractions), len(foods))):
        dest = {}
        
        if idx < len(attractions):
            name, time, budget, duration = attractions[idx]
            dest['place'] = {
                'name': name.strip(),
                'time': time.strip(),
                'budget': budget.strip(),
                'average_timespan': duration.strip()
            }
        
        if idx < len(foods):
            name, budget, duration = foods[idx]
            dest['cuisine'] = {
                'name': name.strip(),
                'budget': budget.strip(),
                'average_timespan': duration.strip()
            }
        
        if dest:
            parsed["Destinations"].append(dest)
    
    # Parse Hotels
    hotel_pattern = r'Hotel:\s*([^,]+),\s*cost category:\s*([^,]+),\s*review quality:\s*([^.]+)'
    hotels = re.findall(hotel_pattern, text)
    
    for name, cost, reviews in hotels:
        parsed["Hotels"].append({
            'name': name.strip(),
            'cost': cost.strip(),
            'reviews': reviews.strip()
        })
    
    # Parse Activities
    activities_pattern = r'Popular activities include:\s*([^.]+)\.'
    activities_match = re.search(activities_pattern, text)
    
    if activities_match:
        activities_text = activities_match.group(1)
        # Split by comma and clean
        activities = [act.strip() for act in activities_text.split(',') if act.strip()]
        parsed["Activities"] = activities
    
    return parsed


# --------------------------------------------------
# Retrieval using ChromaDB Cloud
# --------------------------------------------------
def retrieve_top_k(query, k=10):
    """Retrieve top k locations from ChromaDB Cloud based on query"""
    query_embedding = get_embedding(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    # Extract data from METADATA (not documents - documents are plain text descriptions)
    retrieved_locations = []
    
    if results and results.get("metadatas") and len(results["metadatas"]) > 0:
        metadatas = results["metadatas"][0]
        documents = results["documents"][0]
        
        for idx, metadata in enumerate(metadatas):
            if metadata:
                document_text = documents[idx] if idx < len(documents) else ""
                
                # Parse structured data from document text
                parsed_data = parse_document_text(document_text)
                
                # Extract clean description (not full document)
                clean_description = extract_description(document_text)
                
                # Build location object from metadata and parsed document
                # Match exact format from retrievaled_data_example.json
                location_data = {
                    "Index": metadata.get("index", idx + 1),  # Add Index field
                    "Location name": metadata.get("location_name", ""),
                    "Location": metadata.get("province", ""),
                    "Description": clean_description if clean_description else document_text,
                    "Rating": metadata.get("rating", 0),
                    "Image": metadata.get("image", ""),
                    "Keywords": metadata.get("keywords", ""),
                    "Destinations": parsed_data["Destinations"],
                    "Hotels": parsed_data["Hotels"],
                    "Activities": parsed_data["Activities"]
                }
                retrieved_locations.append(location_data)
    
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
# Public API for external use
# --------------------------------------------------
def initialize_chromadb():
    """
    Verify ChromaDB cloud connection (data already uploaded).
    Call this once before using retrieve_top_k or recommend_locations.
    
    Returns:
        tuple: (collection, total_count)
    """
    count = collection.count()
    print(f"ChromaDB Cloud ready: {count} locations available")
    return collection, count


def get_collection_info():
    """
    Get information about the ChromaDB collection.
    
    Returns:
        dict: Collection metadata including count, name, and cloud status
    """
    return {
        "name": collection.name,
        "count": collection.count(),
        "using_cloud": USE_CLOUD,
        "tenant": os.getenv("CHROMA_TENANT") if USE_CLOUD else None,
        "database": os.getenv("CHROMA_DATABASE") if USE_CLOUD else None,
    }


# --------------------------------------------------
# Main (for testing)
# --------------------------------------------------
if __name__ == "__main__":
    # Test retrieval from ChromaDB Cloud (data already uploaded)
    print(f"Connected to ChromaDB Cloud with {collection.count()} locations\n")
    
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