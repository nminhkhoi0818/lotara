"""
Reset Milvus Collection to Fix Dimension Mismatch
==================================================
Run this script if you encounter vector dimension errors.

This will:
1. Drop the existing collection (if any)
2. Recreate with correct 768-dimension schema
3. Re-upload your tourism data with 768-dim embeddings

IMPORTANT: This will delete all existing data in the collection.
           Make sure you have the source data file available.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.travel_lotara.tools.shared_tools.milvus_engine import (
    create_collection,
    insert_locations,
    get_collection_stats,
    initialize_milvus
)
from src.travel_lotara.config.logging_config import get_logger

logger = get_logger(__name__)


def reset_only():
    """Just reset/recreate the collection without uploading data."""
    logger.info("Recreating Milvus collection with 768 dimensions...")
    create_collection(drop_existing=True)
    logger.info("✅ Collection recreated successfully")
    logger.info("Collection is empty and ready for data upload")
    
    stats = get_collection_stats()
    logger.info(f"Collection stats: {stats}")
    return True


def reset_and_reload():
    """Reset collection and reload data from file."""
    
    # Step 1: Drop existing collection and recreate
    logger.info("Step 1: Recreating Milvus collection with 768 dimensions...")
    create_collection(drop_existing=True)
    logger.info("✅ Collection recreated successfully")
    
    # Step 2: Load Vietnam tourism data
    data_file = project_root / "data" / "VN_tourism.json"
    
    if not data_file.exists():
        logger.warning(f"⚠️  Data file not found: {data_file}")
        logger.info("")
        logger.info("OPTIONS:")
        logger.info("1. The collection has been recreated and is ready")
        logger.info("2. If you have the data file, place it in: data/VN_tourism.json")
        logger.info("3. The data might already be in ChromaDB Cloud (check README)")
        logger.info("4. You can upload data later using insert_locations() function")
        logger.info("")
        logger.info("✅ Collection is ready (empty)")
        return True
    
    logger.info(f"Step 2: Loading data from {data_file}...")
    with open(data_file, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    
    logger.info(f"Found {len(locations)} locations to upload")
    
    # Step 3: Insert locations with embeddings
    logger.info("Step 3: Generating embeddings and uploading to Milvus...")
    logger.info("(This may take a few minutes depending on API rate limits)")
    
    try:
        count = insert_locations(locations)
        logger.info(f"✅ Successfully uploaded {count} locations")
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        logger.info("The collection is still created, you can retry uploading later")
        return False
    
    # Step 4: Verify
    logger.info("Step 4: Verifying collection...")
    stats = get_collection_stats()
    logger.info(f"Collection stats: {stats}")
    
    # Step 5: Test warmup
    logger.info("Step 5: Testing connection with warmup query...")
    try:
        initialize_milvus(warmup=True)
        logger.info("✅ Milvus is ready and working correctly!")
        return True
    except Exception as e:
        logger.error(f"❌ Warmup test failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("MILVUS COLLECTION RESET UTILITY")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This utility fixes vector dimension mismatch errors")
    logger.info("by recreating the collection with 768-dimension schema")
    logger.info("")
    logger.info("⚠️  WARNING: This will delete all existing data in Milvus!")
    logger.info("")
    logger.info("Choose an option:")
    logger.info("1. Reset collection only (recommended if data is already in ChromaDB)")
    logger.info("2. Reset collection and reload from VN_tourism.json file")
    logger.info("3. Cancel")
    logger.info("")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "3" or choice not in ["1", "2"]:
        logger.info("Aborted by user")
        sys.exit(0)
    
    logger.info("")
    
    if choice == "1":
        success = reset_only()
    else:  # choice == "2"
        success = reset_and_reload()
    
    logger.info("")
    logger.info("=" * 60)
    if success:
        logger.info("✅ RESET COMPLETED SUCCESSFULLY")
        logger.info("Your Milvus collection is now using 768-dimension embeddings")
        logger.info("")
        logger.info("NEXT STEPS:")
        logger.info("- The system will now generate 768-dim embeddings automatically")
        logger.info("- ChromaDB Cloud already has your data (362 locations)")
        logger.info("- You can use ChromaDB for retrieval or re-upload to Milvus later")
    else:
        logger.info("❌ OPERATION INCOMPLETE")
        logger.info("Check the logs above for details")
    logger.info("=" * 60)
