# Quick Start Guide

Get AI Studio Proxy API running in 5 minutes!

## 🚀 Installation

```bash
# Clone and setup
git clone https://github.com/lolsZz/AIstudioProxyAPI
cd AIstudioProxyAPI

# Create virtual environment
uv venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Install dependencies
uv install -r requirements.txt
uv install camoufox[geoip]

# Download browser
camoufox fetch

# Start the server
./start.sh
```

## ⚡ Quick Commands

```bash
# Start server (auto mode)
./start.sh

# Test API
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

## 📋 Launch Modes

| Command | Mode | Description |
|---------|------|-------------|
| `./start.sh` | Auto | Smart mode selection |
| `./start.sh headless` | Production | Background operation |
| `./start.sh debug` | Development | Browser window visible |
| `./start.sh auth` | Setup | Authentication only |
| `./start.sh test` | Testing | API endpoint validation |

## 🌐 API Usage

**Base URL**: `http://127.0.0.1:2048/v1`

**Python Example**:
```python
import openai

client = openai.OpenAI(
    base_url="http://127.0.0.1:2048/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="gemini-2.5-pro-preview-06-05",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## 🔍 Troubleshooting

**Server won't start?**
```bash
# Check virtual environment
source .venv/bin/activate

# Re-authenticate if needed
./start.sh auth
```

**API not responding?**
```bash
# Check server status
curl http://127.0.0.1:2048/health

# View logs
tail -f logs/app.log
```

## 📚 More Information

- **Full Documentation**: See `README.md`
- **Detailed Setup**: See `STARTUP_GUIDE.md`
- **Web UI**: Visit `http://127.0.0.1:2048/`

---

**🎉 You're ready to go!** Point any OpenAI-compatible client to `http://127.0.0.1:2048/v1` and start using Google's Gemini models.
