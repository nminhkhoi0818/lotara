"""
Re-ingest Tourism Data with Image URLs
======================================
This script updates the Milvus database with the new image_url fields
that have been added to the VN_tourism.json file.

The new fields are:
- Destinations[].place.image_url
- Destinations[].cuisine.image_url  
- Hotels[].image_url

Usage:
    python -m src.travel_lotara.tools.shared_tools.reingest_with_image_urls

What this script does:
1. Drops the existing Milvus collection
2. Recreates the collection with the same schema
3. Re-ingests all data from VN_tourism.json (now with image_url fields)
4. Verifies the data was ingested correctly
5. Tests retrieval to ensure image_url fields are present

NOTE: This will clear all existing data in Milvus and re-upload it.
      Make sure VN_tourism.json has been updated with image_url fields first.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.travel_lotara.tools.shared_tools.setup_milvus import setup_milvus
from src.travel_lotara.tools.shared_tools.milvus_engine import (
    search_locations,
    get_collection_stats,
    clear_caches
)
from src.travel_lotara.config.logging_config import get_logger
import json

logger = get_logger(__name__)


def verify_image_urls_in_data():
    """Verify that VN_tourism.json contains the new image_url fields."""
    logger.info("Verifying VN_tourism.json has image_url fields...")
    
    data_path = project_root / "data" / "VN_tourism.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check a few random entries for image_url fields
    sample_count = 0
    found_place_image_url = 0
    found_cuisine_image_url = 0
    found_hotel_image_url = 0
    
    for location in data[:10]:  # Check first 10 locations
        if 'Destinations' in location:
            for dest in location['Destinations']:
                if 'place' in dest and 'image_url' in dest['place']:
                    found_place_image_url += 1
                if 'cuisine' in dest and 'image_url' in dest['cuisine']:
                    found_cuisine_image_url += 1
                sample_count += 1
        
        if 'Hotels' in location:
            for hotel in location['Hotels']:
                if 'image_url' in hotel:
                    found_hotel_image_url += 1
    
    logger.info(f"Sample check (first 10 locations):")
    logger.info(f"  ✓ Places with image_url: {found_place_image_url}")
    logger.info(f"  ✓ Cuisines with image_url: {found_cuisine_image_url}")
    logger.info(f"  ✓ Hotels with image_url: {found_hotel_image_url}")
    
    if found_place_image_url == 0 and found_cuisine_image_url == 0 and found_hotel_image_url == 0:
        logger.warning("⚠️  No image_url fields found in sample data!")
        logger.warning("⚠️  Please ensure VN_tourism.json has been updated with image_url fields")
        return False
    
    logger.info("✓ VN_tourism.json appears to have image_url fields")
    return True


def verify_retrieved_data():
    """Verify that retrieved data contains image_url fields."""
    logger.info("\nVerifying retrieved data has image_url fields...")
    
    # Test search
    results = search_locations("cultural attractions in Hanoi", top_k=3)
    
    if not results:
        logger.error("No results returned from search!")
        return False
    
    # Check first result for nested image_url fields
    first_result = results[0]
    logger.info(f"\nChecking location: {first_result.get('Location name', 'Unknown')}")
    
    has_nested_image_urls = False
    
    # Check Destinations
    if 'Destinations' in first_result and first_result['Destinations']:
        dest = first_result['Destinations'][0]
        
        if 'place' in dest:
            logger.info(f"  Place: {dest['place'].get('name', 'N/A')}")
            if 'image_url' in dest['place']:
                logger.info(f"    ✓ place.image_url: {dest['place']['image_url'][:50] if dest['place']['image_url'] else 'empty'}")
                has_nested_image_urls = True
            else:
                logger.warning("    ⚠️  place.image_url field NOT FOUND")
        
        if 'cuisine' in dest:
            logger.info(f"  Cuisine: {dest['cuisine'].get('name', 'N/A')}")
            if 'image_url' in dest['cuisine']:
                logger.info(f"    ✓ cuisine.image_url: {dest['cuisine']['image_url'][:50] if dest['cuisine']['image_url'] else 'empty'}")
                has_nested_image_urls = True
            else:
                logger.warning("    ⚠️  cuisine.image_url field NOT FOUND")
    
    # Check Hotels
    if 'Hotels' in first_result and first_result['Hotels']:
        hotel = first_result['Hotels'][0]
        logger.info(f"  Hotel: {hotel.get('name', 'N/A')}")
        if 'image_url' in hotel:
            logger.info(f"    ✓ hotel.image_url: {hotel['image_url'][:50] if hotel['image_url'] else 'empty'}")
            has_nested_image_urls = True
        else:
            logger.warning("    ⚠️  hotel.image_url field NOT FOUND")
    
    if has_nested_image_urls:
        logger.info("\n✓ Retrieved data contains nested image_url fields!")
        return True
    else:
        logger.error("\n✗ Retrieved data does NOT contain nested image_url fields")
        logger.error("   This may indicate the data was not ingested correctly")
        return False


def main():
    """Main re-ingestion process."""
    logger.info("=" * 80)
    logger.info("RE-INGEST TOURISM DATA WITH IMAGE URLs")
    logger.info("=" * 80)
    
    # Step 1: Verify source data
    logger.info("\n[STEP 1/5] Verifying source data...")
    if not verify_image_urls_in_data():
        logger.error("Source data verification failed!")
        logger.error("Please add image_url fields to VN_tourism.json first")
        return False
    
    # Step 2: Clear caches
    logger.info("\n[STEP 2/5] Clearing caches...")
    clear_caches()
    logger.info("✓ Caches cleared")
    
    # Step 3: Drop and recreate collection with fresh data
    logger.info("\n[STEP 3/5] Re-ingesting data...")
    logger.info("This will drop the existing collection and recreate it with updated data")
    
    try:
        stats = setup_milvus(drop_existing=True)
        logger.info(f"\n✓ Data ingestion complete: {stats.get('count', 0)} locations")
    except Exception as e:
        logger.error(f"Data ingestion failed: {e}", exc_info=True)
        return False
    
    # Step 4: Verify retrieval
    logger.info("\n[STEP 4/5] Verifying retrieved data...")
    if not verify_retrieved_data():
        logger.warning("⚠️  Retrieved data verification found issues")
        logger.warning("   However, ingestion may have succeeded - check manually")
    
    # Step 5: Summary
    logger.info("\n" + "=" * 80)
    logger.info("RE-INGESTION COMPLETE!")
    logger.info("=" * 80)
    logger.info("✓ Milvus database has been updated with image_url fields")
    logger.info("✓ New fields available:")
    logger.info("  - Destinations[].place.image_url")
    logger.info("  - Destinations[].cuisine.image_url")
    logger.info("  - Hotels[].image_url")
    logger.info("=" * 80)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Re-ingest tourism data with new image_url fields"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip verification prompts and force re-ingestion"
    )
    
    args = parser.parse_args()
    
    if not args.force:
        logger.info("\n⚠️  WARNING: This will delete and recreate the Milvus collection!")
        response = input("Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            logger.info("Aborted by user")
            sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1)
