# AIstudioProxyAPI - Quick Start Guide

🎉 **Your AI Studio Proxy API is now ready to use!**

## ✅ What's Working

- **✅ Authentication**: Successfully set up and saved
- **✅ FastAPI Server**: Running on port 2048
- **✅ Stream Proxy**: Running on port 3120  
- **✅ Model Detection**: 15 Gemini models available
- **✅ API Endpoints**: All endpoints responding correctly
- **✅ Startup Scripts**: Easy launch with `./start.sh`

## 🚀 Quick Start Commands

### Start the Server
```bash
# Auto mode (recommended) - chooses best launch mode
./start.sh

# Or force headless mode
./start.sh headless

# Or debug mode with browser
./start.sh debug
```

### Test the API
```bash
# Quick health check
curl http://127.0.0.1:2048/health

# List available models
curl http://127.0.0.1:2048/v1/models

# Test chat completion
curl -X POST http://127.0.0.1:2048/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-2.5-pro-preview-06-05",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

## 📋 Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `./start.sh` | Main launcher | `./start.sh [auto\|headless\|debug\|auth\|test]` |
| `python3 start.py` | Python launcher | `python3 start.py [mode] [options]` |
| `./test_api.sh` | API testing | `./test_api.sh` |

## 🔧 Configuration

### Default Ports
- **FastAPI Server**: 2048
- **Stream Proxy**: 3120

### Custom Ports
```bash
./start.sh headless --server-port 8080 --stream-port 3121
```

### Authentication Files
- **Active**: `auth_profiles/active/` (used by headless mode)
- **Saved**: `auth_profiles/saved/` (backup storage)

## 🌐 API Endpoints

### Base URLs
- **API Base**: `http://127.0.0.1:2048/v1`
- **Health**: `http://127.0.0.1:2048/health`
- **API Info**: `http://127.0.0.1:2048/api/info`

### OpenAI-Compatible Endpoints
- **Models**: `GET /v1/models`
- **Chat Completions**: `POST /v1/chat/completions`
- **Queue Status**: `GET /v1/queue`

## 🎯 Available Models

The API provides access to 15 Gemini models:
- Gemini 2.5 Pro Preview, Flash Preview
- Gemini 2.0 Flash, Flash-Lite
- Gemini 1.5 Pro, Flash, Flash-8B
- Gemma 3 models (1B, 4B, 12B, 27B)
- LearnLM 2.0 Flash Experimental

## 🔄 Common Workflows

### Daily Usage
```bash
# Start server
./start.sh

# Test it's working
curl http://127.0.0.1:2048/health

# Use with your applications
# Point your OpenAI-compatible client to: http://127.0.0.1:2048/v1
```

### Development/Debugging
```bash
# Start in debug mode
./start.sh debug

# Monitor logs in another terminal
tail -f logs/app.log
```

### Re-authentication (when auth expires)
```bash
# Remove old auth
rm auth_profiles/active/*.json

# Re-authenticate
./start.sh auth
```

## 🛠️ Integration Examples

### Python with OpenAI Library
```python
import openai

client = openai.OpenAI(
    base_url="http://127.0.0.1:2048/v1",
    api_key="not-needed"  # No API key required
)

response = client.chat.completions.create(
    model="gemini-2.5-pro-preview-06-05",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### cURL Examples
```bash
# Non-streaming chat
curl -X POST http://127.0.0.1:2048/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-2.5-pro-preview-06-05",
    "messages": [{"role": "user", "content": "Explain quantum computing"}],
    "stream": false,
    "temperature": 0.7,
    "max_output_tokens": 500
  }'

# Streaming chat
curl -X POST http://127.0.0.1:2048/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-2.5-flash-preview-06-05",
    "messages": [{"role": "user", "content": "Write a short story"}],
    "stream": true
  }'
```

## 🔍 Troubleshooting

### Server Not Starting
```bash
# Check virtual environment
source .venv/bin/activate

# Check dependencies
python3 -c "import fastapi, playwright, uvicorn"

# Check authentication
ls auth_profiles/active/
```

### API Not Responding
```bash
# Check if server is running
curl http://127.0.0.1:2048/health

# Check logs
tail -f logs/app.log

# Restart server
./start.sh headless
```

### Authentication Issues
```bash
# Re-authenticate
./start.sh auth

# Or use debug mode
./start.sh debug
```

## 📚 Documentation

- **Detailed Setup**: See `STARTUP_GUIDE.md`
- **API Reference**: See `README.md`
- **Logs**: Check `logs/app.log`

## 🎉 Success!

Your AI Studio Proxy API is now fully operational and ready for production use! The system provides:

- **OpenAI-compatible API** for easy integration
- **Multiple Gemini models** including the latest 2.5 Pro Preview
- **Automatic authentication handling** 
- **Easy startup scripts** for different use cases
- **Comprehensive logging** and monitoring

Start building amazing applications with Google's Gemini models! 🚀
