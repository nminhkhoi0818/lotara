"""
Milvus Data Ingestion Script
=============================
Load Vietnam tourism data from VN_tourism.json into Milvus vector database.

Usage:
    python -m src.travel_lotara.tools.shared_tools.setup_milvus

This script will:
1. Load data from data/VN_tourism.json
2. Create Milvus collection
3. Generate embeddings using Google Gemini
4. Insert all locations into Milvus
5. Verify the data
"""

import os
import json
import sys
from pathlib import Path

# Add project root to path
# File is in: src/travel_lotara/tools/shared_tools/setup_milvus.py
# Need to go up 5 levels to reach project root
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.travel_lotara.tools.shared_tools.milvus_engine import (
    create_collection,
    insert_locations,
    get_collection_stats,
    initialize_milvus,
    search_locations,
)
from src.travel_lotara.config.logging_config import get_logger

logger = get_logger(__name__)


def load_tourism_data(data_path: str = None) -> list:
    """Load tourism data from JSON file."""
    if data_path is None:
        # Default path
        data_path = project_root / "data" / "VN_tourism.json"
    
    logger.info(f"Loading data from: {data_path}")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Loaded {len(data)} locations")
    return data


def setup_milvus(drop_existing: bool = False):
    """
    Main setup function to initialize Milvus with tourism data.
    
    Args:
        drop_existing: If True, drop existing collection and recreate
    """
    logger.info("=" * 70)
    logger.info("MILVUS SETUP - VIETNAM TOURISM DATA")
    logger.info("=" * 70)
    
    # Step 1: Create collection
    logger.info("\n[STEP 1/4] Creating Milvus collection...")
    create_collection(drop_existing=drop_existing)
    
    # Step 2: Check if data already exists
    stats = get_collection_stats()
    if stats['exists'] and stats['count'] > 0 and not drop_existing:
        logger.info(f"\n✓ Collection already has {stats['count']} locations")
        logger.info("  Use drop_existing=True to reload data")
        return stats
    
    # Step 3: Load data
    logger.info("\n[STEP 2/4] Loading tourism data...")
    locations = load_tourism_data()
    
    # Step 4: Insert data (will generate embeddings)
    logger.info("\n[STEP 3/4] Generating embeddings and inserting data...")
    logger.info("  This may take a few minutes...")
    inserted_count = insert_locations(locations)
    
    # Step 5: Verify
    logger.info("\n[STEP 4/4] Verifying data...")
    stats = get_collection_stats()
    
    # Test search
    logger.info("\n" + "=" * 70)
    logger.info("VERIFICATION - TEST SEARCH")
    logger.info("=" * 70)
    
    test_queries = [
        "cultural sites in Hanoi",
        "beach destinations",
        "mountain trekking"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: '{query}'")
        results = search_locations(query, top_k=3)
        
        for i, loc in enumerate(results, 1):
            logger.info(f"  {i}. {loc['Location name']} ({loc['Location']})")
            logger.info(f"     Rating: {loc['Rating']}, Similarity: {loc.get('similarity_score', 0):.3f}")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SETUP COMPLETE!")
    logger.info("=" * 70)
    logger.info(f"✓ Collection: {stats['collection_name']}")
    logger.info(f"✓ Total locations: {stats['count']}")
    logger.info(f"✓ Embedding dimension: {stats['embedding_dim']}")
    logger.info(f"✓ Metric: COSINE similarity")
    logger.info(f"✓ Index: HNSW (M=32, efConstruction=128)")
    logger.info("=" * 70)
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Milvus with Vietnam tourism data")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing collection and recreate"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        help="Path to VN_tourism.json file"
    )
    
    args = parser.parse_args()
    
    try:
        setup_milvus(drop_existing=args.drop)
    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)
        sys.exit(1)
