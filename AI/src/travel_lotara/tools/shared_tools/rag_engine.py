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
import asyncio
import hashlib
import logging
from functools import lru_cache
from typing import Dict, List, Any, Optional, Tuple
from collections import OrderedDict
from google import genai
from dotenv import load_dotenv
from src.travel_lotara.config.logging_config import get_logger

# Load environment variables from .env file (created by chroma db connect)
load_dotenv()

# Logger for this module
logger = get_logger(__name__)

# LRU Cache implementation for better performance
class LRUCache:
    """Thread-safe LRU cache with size limit."""
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)  # Remove oldest
    
    def clear(self) -> None:
        self.cache.clear()
    
    def __len__(self) -> int:
        return len(self.cache)

# Global LRU caches for embeddings and queries
_embedding_cache = LRUCache(max_size=1000)
_query_cache = LRUCache(max_size=500)


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


# GenAI client for embeddings (lazy initialization)
_genai_client: Optional[genai.Client] = None

def get_genai_client() -> genai.Client:
    """Get or create GenAI client (singleton pattern)."""
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(api_key=load_api_key())
    return _genai_client

# -----------------------------
# Initialize ChromaDB Client (Lazy + Singleton)
# -----------------------------
_chroma_client: Optional[chromadb.ClientAPI] = None
_collection = None
USE_CLOUD = True

def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create ChromaDB client (singleton pattern with lazy initialization)."""
    global _chroma_client, USE_CLOUD
    
    if _chroma_client is not None:
        return _chroma_client
    
    # Try Cloud first, fallback to local PersistentClient
    if USE_CLOUD:
        try:
            chroma_api_key = os.getenv("CHROMA_API_KEY")
            chroma_tenant = os.getenv("CHROMA_TENANT")
            chroma_database = os.getenv("CHROMA_DATABASE")
            
            if chroma_api_key and chroma_tenant and chroma_database:
                logger.info(f"Connecting to Chroma Cloud - Tenant: {chroma_tenant}, Database: {chroma_database}")
                
                _chroma_client = chromadb.CloudClient(
                    tenant=chroma_tenant,
                    database=chroma_database,
                    api_key=chroma_api_key
                )
                logger.info("Connected to Chroma Cloud successfully")
                return _chroma_client
            else:
                raise ValueError("Missing CHROMA_API_KEY, CHROMA_TENANT, or CHROMA_DATABASE")

        except Exception as e:
            logger.error(f"Failed to connect to Chroma Cloud: {e}")
            USE_CLOUD = False
    
    if not USE_CLOUD:
        # Use local PersistentClient (works without any cloud setup)
        persist_dir = os.path.join(os.path.dirname(__file__), "chroma_cloud_data")
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
        logger.info(f"Using local ChromaDB storage at: {persist_dir}")
    
    return _chroma_client

def get_collection():
    """Get or create collection with optimized HNSW index parameters."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        
        # Optimized HNSW index parameters for fast retrieval
        # M: Number of bi-directional links (16-64, higher = better recall)
        # ef_construction: Size of dynamic candidate list (100-200, higher = better index)
        # ef_search: Size of dynamic candidate list for search (10-500, higher = better recall)
        metadata = {
            "hnsw:space": "cosine",  # Use cosine similarity
            "hnsw:M": 32,  # Balanced recall/speed
            "hnsw:construction_ef": 128,  # Good index quality
            "hnsw:search_ef": 64,  # Fast search with good recall
        }
        
        try:
            _collection = client.get_or_create_collection(
                name="Lotara",
                metadata=metadata
            )
            logger.info(f"Collection 'Lotara' ready with HNSW optimization. Count: {_collection.count()}")
        except Exception as e:
            # Fallback without metadata if cloud doesn't support it
            logger.warning(f"Could not set HNSW params: {e}")
            _collection = client.get_or_create_collection(name="Lotara")
            logger.info(f"Collection 'Lotara' ready (default config). Count: {_collection.count()}")
    
    return _collection


# -----------------------------
# Embedding function with caching and async support
# -----------------------------
def get_embedding(text: str, model: str = "text-embedding-004") -> List[float]:
    """Generate embedding for query text with LRU caching."""
    # Create hash-based cache key for better collision handling
    cache_key = hashlib.md5(f"{text}_{model}".encode('utf-8')).hexdigest()
    
    # Check cache first
    cached = _embedding_cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Generate embedding
    client = get_genai_client()
    result = client.models.embed_content(model=model, contents=[text])
    vec = result.embeddings[0].values
    
    # Cache the result with LRU eviction
    _embedding_cache.put(cache_key, vec)
    
    return vec

def get_embeddings_batch(texts: List[str], model: str = "text-embedding-004") -> List[List[float]]:
    """Generate embeddings for multiple texts in batch (more efficient)."""
    # Filter cached vs uncached
    results = [None] * len(texts)
    uncached_indices = []
    uncached_texts = []
    
    for idx, text in enumerate(texts):
        cache_key = hashlib.md5(f"{text}_{model}".encode('utf-8')).hexdigest()
        cached = _embedding_cache.get(cache_key)
        if cached is not None:
            results[idx] = cached
        else:
            uncached_indices.append(idx)
            uncached_texts.append(text)
    
    # Batch generate uncached embeddings
    if uncached_texts:
        client = get_genai_client()
        batch_result = client.models.embed_content(model=model, contents=uncached_texts)
        
        for idx, embedding in zip(uncached_indices, batch_result.embeddings):
            vec = embedding.values
            results[idx] = vec
            # Cache it
            cache_key = hashlib.md5(f"{texts[idx]}_{model}".encode('utf-8')).hexdigest()
            _embedding_cache.put(cache_key, vec)
    
    return results

async def get_embedding_async(text: str, model: str = "text-embedding-004") -> List[float]:
    """Async version of get_embedding (runs in thread pool to avoid blocking)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_embedding, text, model)


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
# Retrieval using ChromaDB Cloud with caching
# --------------------------------------------------
def retrieve_top_k(query: str, k: int = 10, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Retrieve top k locations from ChromaDB Cloud with optimized caching and filtering."""
    # Create hash-based cache key
    where_str = json.dumps(where, sort_keys=True) if where else ""
    cache_key = hashlib.md5(f"{query}_{k}_{where_str}".encode('utf-8')).hexdigest()
    
    # Check query cache first
    cached = _query_cache.get(cache_key)
    if cached is not None:
        return cached
    
    query_embedding = get_embedding(query)
    coll = get_collection()
    
    # Optimize query parameters
    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": k,
        "include": ["documents", "metadatas", "distances"]  # Only request needed fields
    }
    
    # Add where filter if provided (narrows search space)
    if where:
        query_params["where"] = where
    
    results = coll.query(**query_params)
    
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
    
    # Cache the results with LRU eviction
    _query_cache.put(cache_key, retrieved_locations)
    
    return retrieved_locations

def retrieve_top_k_batch(queries: List[str], k: int = 10) -> List[List[Dict[str, Any]]]:
    """Retrieve locations for multiple queries in batch (parallel processing)."""
    # Generate embeddings in batch
    embeddings = get_embeddings_batch(queries)
    coll = get_collection()
    
    # Query in batch (more efficient than individual queries)
    results = coll.query(
        query_embeddings=embeddings,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    # Process results for each query
    all_results = []
    for query_idx in range(len(queries)):
        retrieved_locations = []
        
        if results and results.get("metadatas") and query_idx < len(results["metadatas"]):
            metadatas = results["metadatas"][query_idx]
            documents = results["documents"][query_idx]
            
            for idx, metadata in enumerate(metadatas):
                if metadata:
                    document_text = documents[idx] if idx < len(documents) else ""
                    parsed_data = parse_document_text(document_text)
                    clean_description = extract_description(document_text)
                    
                    location_data = {
                        "Index": metadata.get("index", idx + 1),
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
        
        all_results.append(retrieved_locations)
    
    return all_results

async def retrieve_top_k_async(query: str, k: int = 10, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Async version of retrieve_top_k (runs in thread pool to avoid blocking)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, retrieve_top_k, query, k, where)

async def retrieve_top_k_batch_async(queries: List[str], k: int = 10) -> List[List[Dict[str, Any]]]:
    """Async version of retrieve_top_k_batch."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, retrieve_top_k_batch, queries, k)


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
# Generation (STRICT JSON SELECTOR) with async support
# --------------------------------------------------
def recommend_locations(user_query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Synchronous version of recommend_locations."""
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

    client = get_genai_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw_text = response.text

    try:
        return extract_json(raw_text)
    except Exception as e:
        logger.debug(f"RAW LLM OUTPUT:\\n{raw_text}")
        raise e

async def recommend_locations_async(user_query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Async version of recommend_locations (runs in thread pool to avoid blocking)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, recommend_locations, user_query, top_k)


# --------------------------------------------------
# Public API for external use
# --------------------------------------------------
def initialize_chromadb(warmup: bool = True):
    """
    Initialize ChromaDB with optional warmup query for faster first retrieval.
    Call this once at startup before using retrieve_top_k or recommend_locations.
    
    Args:
        warmup: If True, performs a dummy query to warm up the connection
    
    Returns:
        tuple: (collection, total_count)
    """
    coll = get_collection()
    count = coll.count()
    
    # Warmup query to pre-load connection and cache
    if warmup and count > 0:
        try:
            logger.debug("Warming up ChromaDB connection...")
            dummy_embedding = get_embedding("Vietnam tourism")
            coll.query(
                query_embeddings=[dummy_embedding],
                n_results=1,
                include=["metadatas"]
            )
            logger.debug("ChromaDB connection warmed up")
        except Exception as e:
            logger.debug(f"Warmup failed (non-critical): {e}")
    
    logger.info(f"ChromaDB ready: {count} locations available")
    return coll, count

async def initialize_chromadb_async():
    """Async version of initialize_chromadb."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, initialize_chromadb)


def get_collection_info() -> Dict[str, Any]:
    """
    Get information about the ChromaDB collection.
    
    Returns:
        dict: Collection metadata including count, name, and cloud status
    """
    coll = get_collection()
    return {
        "name": coll.name,
        "count": coll.count(),
        "using_cloud": USE_CLOUD,
        "tenant": os.getenv("CHROMA_TENANT") if USE_CLOUD else None,
        "database": os.getenv("CHROMA_DATABASE") if USE_CLOUD else None,
        "cache_stats": {
            "embedding_cache_size": len(_embedding_cache),
            "query_cache_size": len(_query_cache),
        }
    }

def clear_cache():
    """Clear all caches (useful for testing or memory management)."""
    global _embedding_cache, _query_cache
    _embedding_cache.clear()
    _query_cache.clear()
    logger.debug("All ChromaDB caches cleared")

def warmup_cache(common_queries: List[str] = None, k: int = 5):
    """Pre-populate cache with common queries for faster response."""
    if common_queries is None:
        common_queries = [
            "beach destinations in Vietnam",
            "cultural sites in Hanoi",
            "family-friendly activities",
            "mountain trekking locations",
            "historical landmarks"
        ]
    
    logger.info(f"Warming up cache with {len(common_queries)} common queries...")
    for query in common_queries:
        try:
            retrieve_top_k(query, k=k)
        except Exception as e:
            logger.debug(f"Warmup query failed: {query[:30]}... - {e}")
    
    logger.info(f"Cache warmup complete. Query cache size: {len(_query_cache)}")


# --------------------------------------------------
# Main (for testing)
# --------------------------------------------------
if __name__ == "__main__":
    # Test retrieval from ChromaDB Cloud (data already uploaded)
    coll = get_collection()
    logger.info(f"Connected to ChromaDB Cloud with {coll.count()} locations")
    
    user_input = "Give me some place near the Hoan Kiem lake"

    logger.info(f"Analyzing request: '{user_input}'...")

    try:
        results = recommend_locations(user_input, top_k=5)

        logger.info("=" * 50)
        logger.info("LOTARA RECOMMENDATIONS (FROM CHROMA CLOUD)")
        logger.info("=" * 50)
        logger.info(json.dumps(results, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Recommendation error: {e}")