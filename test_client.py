# Test client for CAN Channel Backend Server with FastAPI
import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8000"

def test_fastapi_server():
    """Test the CAN channel backend FastAPI server"""
    print("Testing CAN Channel Backend Server - FastAPI")
    print("=" * 50)
    
    try:
        # Test home endpoint
        print("\n1. Testing home endpoint (GET /):")
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        # Test health endpoint
        print("\n2. Testing health endpoint (GET /health):")
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test channels endpoint
        print("\n3. Testing channels endpoint (GET /channels):")
        response = requests.get(f"{BASE_URL}/channels")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test specific channel endpoint
        print("\n4. Testing specific channel endpoint (GET /channels/0):")
        response = requests.get(f"{BASE_URL}/channels/0")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test sending a CAN message
        print("\n5. Testing CAN message sending (POST /messages/send):")
        message_payload = {
            "channel": 0,
            "can_id": 123,
            "data": [72, 69, 76, 76, 79, 33],  # "HELLO!"
            "bitrate": 250000
        }
        response = requests.post(f"{BASE_URL}/messages/send", json=message_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test starting monitoring
        print("\n6. Testing start monitoring (POST /monitoring/start):")
        monitor_payload = {
            "channel": 1,
            "duration": 10  # 10 seconds
        }
        response = requests.post(f"{BASE_URL}/monitoring/start", json=monitor_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Check monitoring status
        print("\n7. Testing monitoring status (GET /monitoring/status):")
        response = requests.get(f"{BASE_URL}/monitoring/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Send a test message while monitoring
        print("\n8. Sending test message while monitoring:")
        test_message = {
            "channel": 0,
            "can_id": 456,
            "data": [1, 2, 3, 4, 5]
        }
        response = requests.post(f"{BASE_URL}/messages/send", json=test_message)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Wait a bit for monitoring
        print("\n9. Waiting 3 seconds for message monitoring...")
        time.sleep(3)
        
        # Check received messages
        print("\n10. Testing received messages (GET /monitoring/messages):")
        response = requests.get(f"{BASE_URL}/monitoring/messages")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Stop monitoring
        print("\n11. Testing stop monitoring (POST /monitoring/stop):")
        response = requests.post(f"{BASE_URL}/monitoring/stop")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test error cases
        print("\n12. Testing validation errors:")
        
        # Invalid channel
        print("\n    a) Invalid channel error:")
        error_payload = {
            "channel": 999,
            "can_id": 123,
            "data": [1, 2, 3]
        }
        response = requests.post(f"{BASE_URL}/messages/send", json=error_payload)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {json.dumps(response.json(), indent=2)}")
        
        # Invalid data length
        print("\n    b) Invalid data length error:")
        error_payload = {
            "channel": 0,
            "can_id": 123,
            "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Too many bytes
        }
        response = requests.post(f"{BASE_URL}/messages/send", json=error_payload)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {json.dumps(response.json(), indent=2)}")
        
        # Invalid CAN ID
        print("\n    c) Invalid CAN ID error:")
        error_payload = {
            "channel": 0,
            "can_id": 3000,  # Too high for 11-bit CAN ID
            "data": [1, 2, 3]
        }
        response = requests.post(f"{BASE_URL}/messages/send", json=error_payload)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {json.dumps(response.json(), indent=2)}")
        
        # Test non-existent channel
        print("\n13. Testing non-existent channel (GET /channels/999):")
        response = requests.get(f"{BASE_URL}/channels/999")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        print("\n" + "=" * 50)
        print("✅ FastAPI testing completed!")
        print("🌐 Swagger UI: http://localhost:8000/swagger")
        print("📖 ReDoc: http://localhost:8000/redoc")
        print("🏠 Home: http://localhost:8000/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("📝 Make sure the server is running with: python server_fastapi.py")
        print("🌐 Server should be at: http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_openapi_spec():
    """Test OpenAPI specification endpoint"""
    print("\n" + "=" * 50)
    print("TESTING OPENAPI SPECIFICATION")
    print("=" * 50)
    
    try:
        # Test OpenAPI JSON
        print("\n1. Testing OpenAPI JSON (GET /openapi.json):")
        response = requests.get(f"{BASE_URL}/openapi.json")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            openapi_spec = response.json()
            print(f"API Title: {openapi_spec.get('info', {}).get('title', 'Unknown')}")
            print(f"API Version: {openapi_spec.get('info', {}).get('version', 'Unknown')}")
            print(f"Available Paths: {len(openapi_spec.get('paths', {}))}")
            print(f"Available Tags: {[tag['name'] for tag in openapi_spec.get('tags', [])]}")
        
        print("\n✅ OpenAPI specification testing completed!")
        
    except Exception as e:
        print(f"❌ Error testing OpenAPI specification: {str(e)}")

if __name__ == "__main__":
    test_fastapi_server()
    test_openapi_spec()
