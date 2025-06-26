# CAN Channel Backend Server with FastAPI

A comprehensive **FastAPI-based REST API server** with **interactive Swagger UI and ReDoc documentation** for CAN channel management, message sending, and real-time monitoring using the Kvaser canlib library.

## 🚀 FastAPI Features

- **📚 Interactive API Documentation** - Built-in Swagger UI and ReDoc
- **🧪 Built-in API Testing** - Test all endpoints directly in the browser
- **📖 Auto-generated Documentation** - Schema validation with Pydantic models
- **🔍 API Explorer** - Discover and understand all available endpoints
- **✅ Request/Response Validation** - Automatic data validation with clear error messages
- **📊 Organized Endpoints** - Logical grouping with tags
- **⚡ High Performance** - FastAPI's speed and async capabilities
- **🔒 Type Safety** - Full type hints and validation

## 📁 Project Files

- `server.py` - **FastAPI server** with Swagger UI and ReDoc
- `test_client.py` - API test client for all endpoints
- `web_interface.html` - Web control panel for browser-based testing
- `start_server.bat` - Server launcher script
- `check_ch.py` - Channel checking script (reference)
- `send_msg.py` - CAN message sending example (reference)
- `requirements.txt` - FastAPI dependencies

## 🛠️ Installation

1. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Option 1: Use the Swagger launcher (Recommended)
```cmd
start_swagger_server.bat
```

### Option 2: Manual start
```cmd
python server_swagger.py
```

### Option 3: Access the interfaces
1. **Swagger UI**: http://localhost:5000/swagger/
2. **Home Page**: http://localhost:5000/
3. **API Endpoints**: http://localhost:5000/api/

## 📚 FastAPI Documentation

### 🌐 Access Points
- **Swagger UI**: `http://localhost:8000/swagger`
- **ReDoc**: `http://localhost:8000/redoc`
- **Home Page**: `http://localhost:8000/`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### 🔧 What You Can Do in the Documentation
1. **Explore all API endpoints** with detailed documentation
2. **Test API calls** directly in the browser (Swagger UI)
3. **View request/response schemas** with Pydantic models
4. **Validate input data** with real-time feedback
5. **Download API specification** (OpenAPI 3.0 JSON)
6. **Browse beautiful documentation** (ReDoc)

## 📡 API Structure (Organized with Tags)

### 🏷️ Channels (`/channels`)
- **GET /channels** - Get all available CAN channels
- **GET /channels/{channel_id}** - Get specific channel information

### 📤 Messages (`/messages`)
- **POST /messages/send** - Send a CAN message

### 📥 Monitoring (`/monitoring`)
- **POST /monitoring/start** - Start CAN message monitoring
- **POST /monitoring/stop** - Stop CAN message monitoring
- **GET /monitoring/messages** - Get received messages
- **GET /monitoring/status** - Get monitoring status

### 🔧 System (`/`)
- **GET /** - Home page with navigation
- **GET /health** - Server health check

## 📊 Pydantic Model Validation

### Example: Send Message Request
```json
{
  "channel": 0,
  "can_id": 123,
  "data": [72, 69, 76, 76, 79, 33],
  "bitrate": 250000
}
```

**Validation Rules:**
- `channel`: Integer, 0-3 (validates against available channels)
- `can_id`: Integer, 0-2047 (11-bit CAN ID)
- `data`: Array of integers, max 8 bytes, each 0-255
- `bitrate`: Optional integer, default 250000

### Example: Error Response
```json
{
  "status": "error",
  "message": "Invalid channel 999. Available channels: 0-3"
}
```

## 🧪 Testing

### Test with the Swagger test client
```cmd
python test_swagger.py
```

### Test in Swagger UI
1. Open http://localhost:8000/swagger
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. View the results

### Test with curl
```bash
# Get all channels
curl http://localhost:8000/channels

# Send a message
curl -X POST http://localhost:8000/messages/send \
  -H "Content-Type: application/json" \
  -d '{"channel": 0, "can_id": 123, "data": [1,2,3,4,5]}'

# Start monitoring
curl -X POST http://localhost:8000/monitoring/start \
  -H "Content-Type: application/json" \
  -d '{"channel": 1, "duration": 30}'
```

### Test with Python
```python
import requests

# Get all channels
response = requests.get("http://localhost:8000/channels")
print(response.json())

# Send a message
message_data = {
    "channel": 0,
    "can_id": 123,
    "data": [72, 69, 76, 76, 79, 33]
}
response = requests.post("http://localhost:8000/messages/send", json=message_data)
print(response.json())
```

## 🌐 FastAPI Documentation Interface

When you open the Swagger UI, you'll see:

1. **API Information** - Title, version, and description
2. **Endpoint Groups** - Organized by functionality:
   - 🏷️ **Channels** - Channel discovery and info
   - 📤 **Messages** - Message sending operations  
   - 📥 **Monitoring** - Message monitoring operations
   - 🔧 **System** - Health and status endpoints
3. **Endpoint Details** - Click to expand each endpoint
4. **Try It Out** - Interactive testing interface
5. **Request/Response Examples** - Sample data and schemas

## 🔧 Advanced Features

### Schema Validation
All requests are validated against predefined schemas:
- **Automatic type checking**
- **Range validation** (e.g., channel 0-3, CAN ID 0-2047)
- **Required field validation**
- **Data format validation**

### Error Handling
Comprehensive error responses with:
- **HTTP status codes** (400, 404, 500)
- **Detailed error messages**
- **Validation error details**
- **Suggested corrections**

### API Documentation
Auto-generated documentation includes:
- **Parameter descriptions**
- **Example requests/responses**
- **Error code explanations**
- **Data type specifications**

## 📈 Production Deployment

For production use with Swagger UI:

```python
# Disable debug mode and restrict Swagger access
if app.config.get('ENV') == 'production':
    api.doc = False  # Disable Swagger UI in production
```

Or use environment-based configuration:
```bash
export FLASK_ENV=production
python server_swagger.py
```

## 🔄 Migration from Original Server

Both servers can run simultaneously on different ports:

```python
# Original server (port 5000)
python server.py

# Swagger server (port 5001)  
app.run(host='0.0.0.0', port=5001, debug=True)
```

## 📋 Comparison: Original vs Swagger

| Feature | Original Server | Swagger Server |
|---------|----------------|----------------|
| API Endpoints | ✅ | ✅ |
| Web Interface | ✅ | ✅ |
| Interactive Docs | ❌ | ✅ |
| Request Validation | Basic | Advanced |
| Error Messages | Simple | Detailed |
| API Testing | External tools | Built-in |
| Schema Documentation | Manual | Auto-generated |
| Organized Structure | Flat | Namespaced |

## 🤝 Integration Examples

### JavaScript/Web App
```javascript
// Using fetch with proper error handling
const sendMessage = async (channel, canId, data) => {
  try {
    const response = await fetch('/api/messages/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel, can_id: canId, data })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to send message:', error.message);
  }
};
```

### Python Client
```python
import requests

class CANClient:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
    
    def get_channels(self):
        response = requests.get(f"{self.base_url}/channels/")
        response.raise_for_status()
        return response.json()
    
    def send_message(self, channel, can_id, data):
        payload = {"channel": channel, "can_id": can_id, "data": data}
        response = requests.post(f"{self.base_url}/messages/send", json=payload)
        response.raise_for_status()
        return response.json()

# Usage
client = CANClient()
channels = client.get_channels()
result = client.send_message(0, 123, [1, 2, 3, 4, 5])
```

## 🎯 Next Steps

1. **Explore the Swagger UI** at http://localhost:5000/swagger/
2. **Test the API** using the interactive interface
3. **Integrate with your applications** using the documented endpoints
4. **Customize the API** by modifying the Swagger schemas
5. **Deploy to production** with proper security configurations

## 🆘 Troubleshooting

### Common Issues
- **Swagger UI not loading**: Check if flask-restx is installed
- **API validation errors**: Review the request schema in Swagger UI
- **CORS issues**: CORS is enabled by default for web apps
- **Port conflicts**: Change the port in server_swagger.py if needed

### Debug Mode
The server runs in debug mode by default, providing:
- **Automatic reloading** on code changes
- **Detailed error traces** in the browser
- **Interactive debugger** for development
