# CAN Channel Backend Project

A clean, professional CAN channel management system with FastAPI, Swagger UI, and ReDoc.

## 📁 Project Structure

```
python_kvaser/
├── .venv/              # Virtual environment
├── .vscode/            # VS Code configuration
├── .gitignore          # Git ignore file
├── server.py           # FastAPI server with Swagger UI & ReDoc
├── start_server.bat    # Server launcher script
├── test_client.py      # FastAPI API test client
├── web_interface.html  # Web control panel
├── requirements.txt    # FastAPI dependencies
├── README.md          # Complete documentation
├── PROJECT_SUMMARY.md  # Quick project overview
```

## 🚀 Quick Start

1. **Start the server:**
   ```cmd
   start_server.bat
   ```

2. **Access Documentation:**
   - **Swagger UI**: http://localhost:8000/swagger
   - **ReDoc**: http://localhost:8000/redoc
   - **Home Page**: http://localhost:8000/

3. **Test the API:**
   ```cmd
   python test_client.py
   ```

4. **Use Web Interface:**
   - Open `web_interface.html` in your browser

## 📚 Key Features

- ✅ **Interactive FastAPI Documentation** - Swagger UI + ReDoc
- ✅ **High Performance** - FastAPI's speed and async capabilities
- ✅ **Type Safety** - Pydantic models with full validation
- ✅ **CAN Channel Discovery** and management
- ✅ **Message Sending** with comprehensive validation
- ✅ **Real-time Monitoring** capabilities
- ✅ **Professional API** with proper error handling
- ✅ **CORS Support** for web applications

## 🔧 Dependencies

- FastAPI (Modern, fast web framework)
- Uvicorn (ASGI server)
- Pydantic (Data validation and settings)
- Kvaser canlib (CAN interface)
- Requests (HTTP client for testing)

## 📖 Documentation

See `README.md` for complete documentation including:
- FastAPI endpoints and examples
- Swagger UI & ReDoc usage guide
- Pydantic model validation
- Integration examples
- Troubleshooting tips
