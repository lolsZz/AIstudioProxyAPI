# Startup Guide

Complete guide for launching AI Studio Proxy API with different modes and configurations.

## 🚀 Quick Launch

```bash
# Make script executable (first time only)
chmod +x start.sh

# Start server (auto mode)
./start.sh

# Or specify mode
./start.sh headless    # Production mode
./start.sh debug       # Development mode
./start.sh auth        # Authentication setup
./start.sh test        # API testing
```

## 🔧 Cross-Platform Options

**Linux/macOS (Recommended)**:
```bash
./start.sh [mode] [options]
```

**Windows/Cross-platform**:
```bash
python3 start.py [mode] [options]
```

## 📋 Launch Modes

| Mode | Command | Description |
|------|---------|-------------|
| **Auto** | `./start.sh` | Smart mode selection (recommended) |
| **Headless** | `./start.sh headless` | Production mode (no browser window) |
| **Debug** | `./start.sh debug` | Development mode (browser visible) |
| **Auth** | `./start.sh auth` | Authentication setup only |
| **Test** | `./start.sh test` | API endpoint testing |

## ⚙️ Configuration Options

**Custom Ports:**
```bash
./start.sh headless --server-port 8080 --stream-port 3121
```

**Environment Variables:**
```bash
export SERVER_PORT=8080
export STREAM_PORT=3121
export DEBUG_LOGS_ENABLED=true
./start.sh
```

**Help:**
```bash
./start.sh --help
```

## 🔐 Authentication Setup

**First time setup:**
```bash
./start.sh auth
```

1. Complete Google login in browser
2. Navigate to AI Studio chat interface
3. Authentication files saved automatically

**When authentication expires:**
```bash
rm auth_profiles/active/*.json
./start.sh auth
```

## 🌐 API Usage

**Base URL**: `http://127.0.0.1:2048/v1`

**Test endpoints:**
```bash
# Health check
curl http://127.0.0.1:2048/health

# List models
curl http://127.0.0.1:2048/v1/models

# Chat completion
curl -X POST http://127.0.0.1:2048/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-2.5-pro-preview-06-05",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

## 🔧 Troubleshooting

**Virtual environment issues:**
```bash
uv venv .venv
source .venv/bin/activate
uv install -r requirements.txt
```

**Authentication problems:**
```bash
./start.sh auth
```

**Port conflicts:**
```bash
./start.sh headless --server-port 8080
```

**API not responding:**
```bash
./start.sh test
```

## 🚀 Production Deployment

**Systemd service:**
```ini
[Unit]
Description=AI Studio Proxy API
After=network.target

[Service]
Type=simple
User=aistudio
WorkingDirectory=/opt/aistudio-proxy
ExecStart=/opt/aistudio-proxy/start.sh headless
Restart=always

[Install]
WantedBy=multi-user.target
```

---

**📚 For complete documentation, see `README.md`**
