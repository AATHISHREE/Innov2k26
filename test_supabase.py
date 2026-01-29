import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

print("🔗 TESTING SUPABASE CONNECTION")
print("=" * 50)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key: {key[:20]}...")

try:
    from supabase import create_client
    supabase = create_client(url, key)
    
    # Test 1: Simple query
    print("\\n✅ Supabase client created successfully!")
    
    # Test 2: Check if table exists
    try:
        response = supabase.table("heart_screenings").select("id", count="exact").limit(1).execute()
        print("✅ 'heart_screenings' table exists!")
    except Exception as e:
        print(f"⚠️ Table check: {str(e)[:100]}")
        print("   Run the SQL in Supabase SQL Editor to create table")
    
    # Test 3: Insert test record
    test_data = {
        "patient_id": "connection_test",
        "patient_name": "Connection Test",
        "prediction": "normal",
        "confidence": 0.85,
        "risk_level": "low"
    }
    
    try:
        insert_response = supabase.table("heart_screenings").insert(test_data).execute()
        if hasattr(insert_response, 'data') and insert_response.data:
            print(f"✅ Test record inserted! ID: {insert_response.data[0].get('id', 'unknown')}")
            
            # Clean up
            if insert_response.data[0].get('id'):
                supabase.table("heart_screenings").delete().eq("id", insert_response.data[0]['id']).execute()
                print("✅ Test record cleaned up")
    except Exception as e:
        print(f"⚠️ Insert test: {str(e)[:100]}")
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)[:100]}")

print("=" * 50)
