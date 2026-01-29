import requests
import json

def test_backend():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Backend...")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check:")
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        data = resp.json()
        print(f"   Status: {resp.status_code}")
        print(f"   ML Status: {data.get('ml_integration', {})}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Mock analysis
    print("\n2. Mock Analysis:")
    try:
        resp = requests.post(f"{base_url}/mock-analyze", 
                           json={"patient_id": "TEST001", "age": 30, "gender": "female"},
                           timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Result: {resp.json().get('prediction')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test Complete!")

if __name__ == "__main__":
    test_backend()
