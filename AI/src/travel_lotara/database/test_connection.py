#!/usr/bin/env python
"""
Test Supabase Connection

Quick script to verify Supabase is properly configured and connected.

Usage:
    python -m travel_lotara.database.test_connection
"""

import os
import sys
from datetime import datetime


def test_connection():
    """Test Supabase connection and basic operations."""
    print("=" * 50)
    print("Supabase Connection Test")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url:
        print("   ❌ SUPABASE_URL not set")
        return False
    else:
        print(f"   ✓ SUPABASE_URL: {url[:30]}...")
    
    if not anon_key and not service_key:
        print("   ❌ No Supabase key found (SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY)")
        return False
    else:
        key_type = "SUPABASE_SERVICE_ROLE_KEY" if service_key else "SUPABASE_ANON_KEY"
        print(f"   ✓ {key_type}: ***{(anon_key or service_key)[-10:]}")
    
    # Import and test client
    print("\n2. Testing Supabase client...")
    try:
        from travel_lotara.database import get_supabase_client
        client = get_supabase_client()
        print("   ✓ Client initialized successfully")
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Run: pip install supabase")
        return False
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        return False
    
    # Test health check
    print("\n3. Testing database connectivity...")
    try:
        health = client.health_check()
        if health["connected"]:
            print(f"   ✓ {health['message']}")
        else:
            print(f"   ⚠ {health['message']}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test basic table access
    print("\n4. Testing table access...")
    try:
        # Try to query jobs table
        response = client.table("jobs").select("count").limit(1).execute()
        print("   ✓ Jobs table accessible")
    except Exception as e:
        error_msg = str(e).lower()
        if "does not exist" in error_msg or "permission denied" in error_msg:
            print("   ⚠ Jobs table not found - run migrations first")
            print("   See: src/travel_lotara/database/migrations/README.md")
        else:
            print(f"   ❌ Table access error: {e}")
    
    # Test repository
    print("\n5. Testing repository pattern...")
    try:
        from travel_lotara.database import JobRepository
        repo = JobRepository()
        print("   ✓ JobRepository initialized")
    except Exception as e:
        print(f"   ⚠ Repository initialization: {e}")
    
    print("\n" + "=" * 50)
    print("Connection test complete!")
    print("=" * 50)
    
    print("\nNext steps:")
    print("1. Run the SQL migration in Supabase SQL Editor")
    print("2. Update your .env with actual Supabase credentials")
    print("3. Start using the database in your application")
    
    return True


if __name__ == "__main__":
    # Load .env file if exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file\n")
    except ImportError:
        print("Note: python-dotenv not installed, using system environment\n")
    
    success = test_connection()
    sys.exit(0 if success else 1)
