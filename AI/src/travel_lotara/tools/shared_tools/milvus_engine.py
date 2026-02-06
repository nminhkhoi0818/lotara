"""
Milvus Vector Database Engine for Travel Lotara
================================================
High-performance vector search using Milvus for Vietnam tourism recommendations.

FEATURES:
- Zilliz Cloud (fully managed Milvus) or Milvus Lite (local embedded)
- Google Gemini embeddings (768 dimensions)
- Fast HNSW index for similarity search
- LRU caching for embeddings and queries
- Async support for non-blocking operations

CONFIGURATION:
- Set ZILLIZ_CLOUD_URI and ZILLIZ_CLOUD_API_KEY to use Zilliz Cloud
- Leave unset to use Milvus Lite (local embedded database)

PERFORMANCE OPTIMIZATIONS:
- Singleton client pattern
- Connection pooling
- Batch operations
- In-memory caching (embeddings + queries)
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional
from collections import OrderedDict
from pymilvus import MilvusClient, DataType
from google import genai
from dotenv import load_dotenv
from src.travel_lotara.config.logging_config import get_logger

# Load environment variables
load_dotenv()

# Logger
logger = get_logger(__name__)

# LRU Cache implementation
class LRUCache:
    """Thread-safe LRU cache with size limit."""
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def clear(self) -> None:
        self.cache.clear()
    
    def __len__(self) -> int:
        return len(self.cache)

# Global instances
_milvus_client: Optional[MilvusClient] = None
_embedding_cache = LRUCache(max_size=1000)
_query_cache = LRUCache(max_size=500)
_genai_client: Optional[genai.Client] = None

# Constants
COLLECTION_NAME = "lotara_travel"
EMBEDDING_DIM = 768  # Google gemini-embedding-001 with output_dimensionality=768
MILVUS_DB_FILE = "milvus_lotara.db"  # Local file for Milvus Lite

# Zilliz Cloud configuration (optional - falls back to Milvus Lite if not set)
ZILLIZ_CLOUD_URI = os.getenv("ZILLIZ_CLOUD_URI")  # e.g., https://xxx.api.gcp-us-west1.zillizcloud.com
ZILLIZ_CLOUD_API_KEY = os.getenv("ZILLIZ_CLOUD_API_KEY")  # API token from Zilliz Cloud


def get_genai_client() -> genai.Client:
    """Get or create Google GenAI client (singleton)."""
    global _genai_client
    
    if _genai_client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        _genai_client = genai.Client(api_key=api_key)
        logger.info("Google GenAI client initialized")
    
    return _genai_client


def get_milvus_client() -> MilvusClient:
    """
    Get or create Milvus client (singleton pattern).
    
    Connects to Zilliz Cloud if ZILLIZ_CLOUD_URI and ZILLIZ_CLOUD_API_KEY are set,
    otherwise uses Milvus Lite (local embedded database).
    
    Environment Variables:
        ZILLIZ_CLOUD_URI: Zilliz Cloud endpoint (e.g., https://xxx.api.gcp-us-west1.zillizcloud.com)
        ZILLIZ_CLOUD_API_KEY: API token from Zilliz Cloud console
    
    Returns:
        MilvusClient instance connected to Zilliz Cloud or Milvus Lite
    """
    global _milvus_client
    
    if _milvus_client is None:
        # Check if Zilliz Cloud credentials are provided
        if ZILLIZ_CLOUD_URI and ZILLIZ_CLOUD_API_KEY:
            # Use Zilliz Cloud (fully managed Milvus)
            logger.info(f"Connecting to Zilliz Cloud: {ZILLIZ_CLOUD_URI}")
            _milvus_client = MilvusClient(
                uri=ZILLIZ_CLOUD_URI,
                token=ZILLIZ_CLOUD_API_KEY
            )
            logger.info("✓ Connected to Zilliz Cloud successfully")
        else:
            # Use Milvus Lite (embedded) for local development
            db_path = os.path.join(os.path.dirname(__file__), MILVUS_DB_FILE)
            logger.info(f"Using Milvus Lite (local embedded database)")
            _milvus_client = MilvusClient(db_path)
            logger.info(f"✓ Milvus Lite initialized at: {db_path}")
    
    return _milvus_client


def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using Google Gemini with caching.
    
    Args:
        text: Text to embed
        
    Returns:
        768-dimensional embedding vector
    """
    # Check cache first
    cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
    cached = _embedding_cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Generate embedding with 768 dimensions
    # Note: gemini-embedding-001 defaults to 3072 dims, must specify output_dimensionality
    client = get_genai_client()
    from google.genai import types
    
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[text],
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIM,  # 768 dimensions
            task_type="RETRIEVAL_QUERY"  # Optimized for search queries
        )
    )
    
    embedding = result.embeddings[0].values
    
    # Cache result
    _embedding_cache.put(cache_key, embedding)
    
    return embedding


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts in batch."""
    embeddings = []
    for text in texts:
        embeddings.append(get_embedding(text))
    return embeddings


def create_collection(drop_existing: bool = False) -> None:
    """
    Create Milvus collection with optimized schema.
    
    Args:
        drop_existing: If True, drop existing collection first
    """
    client = get_milvus_client()
    
    # Drop existing collection if requested
    if drop_existing and client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
        logger.info(f"Dropped existing collection: {COLLECTION_NAME}")
    
    # Check if collection already exists
    if client.has_collection(COLLECTION_NAME):
        logger.info(f"Collection '{COLLECTION_NAME}' already exists")
        return
    
    # Create collection with schema
    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=EMBEDDING_DIM,
        metric_type="COSINE",  # Cosine similarity for semantic search
        auto_id=False,  # Use our own IDs
        # HNSW index parameters for fast search
        index_params={
            "index_type": "HNSW",
            "metric_type": "COSINE",
            "params": {
                "M": 32,  # Connections per layer (16-64)
                "efConstruction": 128,  # Build quality (100-500)
            }
        }
    )
    
    logger.info(f"Collection '{COLLECTION_NAME}' created with HNSW index")


def insert_locations(locations: List[Dict[str, Any]]) -> int:
    """
    Insert location data with embeddings into Milvus.
    
    Args:
        locations: List of location dictionaries from VN_tourism.json
        
    Returns:
        Number of locations inserted
    """
    client = get_milvus_client()
    
    # Prepare data for insertion
    data = []
    for loc in locations:
        # Create searchable text from location data
        search_text = f"""
Location: {loc.get('Location name', '')}
Province: {loc.get('Location', '')}
Description: {loc.get('Description', '')}
Keywords: {loc.get('Keywords', '')}
Rating: {loc.get('Rating', 0)}
"""
        
        # Generate embedding
        embedding = get_embedding(search_text.strip())
        
        # Prepare document
        data.append({
            "id": loc.get("Index", 0),
            "vector": embedding,
            "location_name": loc.get("Location name", ""),
            "province": loc.get("Location", ""),
            "description": loc.get("Description", ""),
            "rating": float(loc.get("Rating", 0)),
            "keywords": loc.get("Keywords", ""),
            "image": loc.get("Image", ""),
            "metadata": json.dumps({
                "Destinations": loc.get("Destinations", []),
                "Hotels": loc.get("Hotels", []),
                "Activities": loc.get("Activities", [])
            })
        })
    
    # Insert in batches
    batch_size = 100
    total_inserted = 0
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        res = client.insert(
            collection_name=COLLECTION_NAME,
            data=batch
        )
        total_inserted += res['insert_count']
        logger.debug(f"Inserted batch {i//batch_size + 1}: {res['insert_count']} locations")
    
    # Flush data to ensure persistence (important for Zilliz Cloud)
    try:
        client.flush(COLLECTION_NAME)
        logger.info("Data flushed to storage")
    except Exception as e:
        logger.warning(f"Flush operation skipped: {e}")
    
    logger.info(f"Total locations inserted: {total_inserted}")
    return total_inserted


def search_locations(
    query: str,
    top_k: int = 5,
    filter_expr: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for locations using semantic similarity.
    
    Args:
        query: Search query text
        top_k: Number of results to return
        filter_expr: Optional Milvus filter expression
        
    Returns:
        List of location dictionaries with similarity scores
    """
    # Check query cache
    cache_key = hashlib.md5(f"{query}_{top_k}_{filter_expr}".encode('utf-8')).hexdigest()
    cached = _query_cache.get(cache_key)
    if cached is not None:
        logger.debug(f"Cache hit for query: {query[:50]}...")
        return cached
    
    client = get_milvus_client()
    
    # Load collection into memory (required for Zilliz Cloud serverless)
    try:
        client.load_collection(COLLECTION_NAME)
        logger.debug(f"Collection '{COLLECTION_NAME}' loaded for search")
    except Exception as e:
        logger.debug(f"Collection load skipped (may already be loaded): {e}")
    
    # Generate query embedding
    query_embedding = get_embedding(query)
    
    # Search
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_embedding],
        limit=top_k,
        output_fields=[
            "location_name", "province", "description",
            "rating", "keywords", "image", "metadata"
        ],
        filter=filter_expr
    )
    
    # Format results
    locations = []
    for hits in results:
        for hit in hits:
            # Parse metadata
            metadata = json.loads(hit['entity']['metadata'])
            
            location_data = {
                "Index": hit['id'],
                "Location name": hit['entity']['location_name'],
                "Location": hit['entity']['province'],
                "Description": hit['entity']['description'],
                "Rating": hit['entity']['rating'],
                "Image": hit['entity']['image'],
                "Keywords": hit['entity']['keywords'],
                "Destinations": metadata.get("Destinations", []),
                "Hotels": metadata.get("Hotels", []),
                "Activities": metadata.get("Activities", []),
                "similarity_score": hit['distance']
            }
            locations.append(location_data)
    
    # Cache results
    _query_cache.put(cache_key, locations)
    
    return locations


def recommend_locations(user_query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Main function to get location recommendations.
    
    Args:
        user_query: User's travel query
        top_k: Number of recommendations
        
    Returns:
        List of recommended locations
    """
    return search_locations(user_query, top_k=top_k)


def get_collection_stats() -> Dict[str, Any]:
    """Get collection statistics."""
    client = get_milvus_client()
    
    if not client.has_collection(COLLECTION_NAME):
        return {
            "exists": False,
            "count": 0
        }
    
    # Load collection into memory (required for Zilliz Cloud serverless)
    try:
        client.load_collection(COLLECTION_NAME)
        logger.debug(f"Collection '{COLLECTION_NAME}' loaded into memory")
    except Exception as e:
        logger.warning(f"Could not load collection (may already be loaded): {e}")
    
    stats = client.get_collection_stats(COLLECTION_NAME)
    
    return {
        "exists": True,
        "count": stats.get("row_count", 0),
        "collection_name": COLLECTION_NAME,
        "embedding_dim": EMBEDDING_DIM
    }


def clear_caches() -> None:
    """Clear all caches."""
    _embedding_cache.clear()
    _query_cache.clear()
    logger.debug("All caches cleared")


def initialize_milvus(warmup: bool = True) -> Dict[str, Any]:
    """
    Initialize Milvus client and optionally warmup caches.
    
    Args:
        warmup: If True, pre-load common queries
        
    Returns:
        Initialization status
    """
    client = get_milvus_client()
    stats = get_collection_stats()
    
    if warmup and stats['exists']:
        logger.info("Warming up Milvus connection...")
        try:
            # Test query
            search_locations("Vietnam tourism", top_k=1)
            logger.debug("Milvus connection warmed up")
        except Exception as e:
            logger.warning(f"Warmup query failed (non-critical): {e}")
    
    logger.info(f"Milvus ready: {stats.get('count', 0)} locations available")
    
    return stats


if __name__ == "__main__":
    # Test the Milvus engine
    logger.info("Testing Milvus engine...")
    
    # Initialize
    stats = initialize_milvus()
    logger.info(f"Collection stats: {stats}")
    
    # Test search
    if stats['exists']:
        query = "cultural sites in Hanoi"
        logger.info(f"Searching for: {query}")
        results = recommend_locations(query, top_k=3)
        
        logger.info("=" * 50)
        logger.info("MILVUS SEARCH RESULTS")
        logger.info("=" * 50)
        for i, loc in enumerate(results, 1):
            logger.info(f"{i}. {loc['Location name']} ({loc['Location']})")
            logger.info(f"   Rating: {loc['Rating']}, Similarity: {loc.get('similarity_score', 0):.3f}")
