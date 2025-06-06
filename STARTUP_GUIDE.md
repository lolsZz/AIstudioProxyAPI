# AIstudioProxyAPI Startup Guide

This guide provides easy-to-use startup scripts for running the AI Studio Proxy API with minimal configuration.

## Quick Start

### Option 1: Bash Script (Recommended for Linux/macOS)
```bash
# Make executable (first time only)
chmod +x start.sh

# Auto mode - automatically chooses best launch mode
./start.sh

# Or specify mode explicitly
./start.sh headless
./start.sh debug
```

### Option 2: Python Script (Cross-platform)
```bash
# Auto mode
python3 start.py

# Or specify mode explicitly
python3 start.py headless
python3 start.py debug
```

## Available Launch Modes

### 1. Auto Mode (Default)
```bash
./start.sh auto          # or just ./start.sh
python3 start.py auto    # or just python3 start.py
```
- **Smart mode**: Automatically chooses the best launch mode
- If authentication is available → runs in **headless mode**
- If no authentication → runs in **debug mode** for initial setup

### 2. Headless Mode
```bash
./start.sh headless
python3 start.py headless
```
- **Production mode**: Runs without browser window
- **Requires**: Valid authentication file in `auth_profiles/active/`
- **Best for**: Server deployment, automated usage
- **Ports**: FastAPI on 2048, Stream proxy on 3120

### 3. Debug Mode
```bash
./start.sh debug
python3 start.py debug
```
- **Development mode**: Opens browser window for interaction
- **Use for**: Initial authentication setup, debugging
- **Interactive**: Allows manual Google login and testing

### 4. Authentication Setup
```bash
./start.sh auth
python3 start.py auth
```
- **Setup mode**: Runs authentication process only
- Opens browser for Google AI Studio login
- Saves authentication for future headless use

### 5. Test Mode
```bash
./start.sh test
python3 start.py test
```
- **Testing mode**: Tests API endpoints without starting server
- Checks if server is running and responding
- Useful for health checks and validation

## Command Line Options

### Port Configuration
```bash
# Custom server port
./start.sh headless --server-port 8080

# Custom stream proxy port  
./start.sh headless --stream-port 3121

# Both custom ports
./start.sh headless --server-port 8080 --stream-port 3121
```

### Help
```bash
./start.sh --help
python3 start.py --help
```

## Authentication Setup Process

### First Time Setup
1. **Run authentication mode**:
   ```bash
   ./start.sh auth
   ```

2. **Complete Google login** in the opened browser window

3. **Navigate to AI Studio** and ensure you see the chat interface

4. **Save authentication** when prompted

5. **Authentication file** will be automatically moved to active directory

### Authentication File Management
- **Active**: `auth_profiles/active/` - Used by headless mode
- **Saved**: `auth_profiles/saved/` - Backup storage
- **Auto-move**: Scripts automatically move saved → active when needed

## API Endpoints

Once running, the API provides these endpoints:

### Base URLs
- **API Base**: `http://127.0.0.1:2048/v1`
- **Health Check**: `http://127.0.0.1:2048/health`
- **API Info**: `http://127.0.0.1:2048/api/info`

### OpenAI-Compatible Endpoints
```bash
# List available models
curl http://127.0.0.1:2048/v1/models

# Chat completion (non-streaming)
curl -X POST http://127.0.0.1:2048/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-2.5-pro-preview-06-05",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'

# Chat completion (streaming)
curl -X POST http://127.0.0.1:2048/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-2.5-pro-preview-06-05", 
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "stream": true
  }'
```

## Troubleshooting

### Common Issues

#### 1. Virtual Environment Not Found
```
[ERROR] Virtual environment not found at .venv
```
**Solution**:
```bash
uv venv .venv
source .venv/bin/activate  
uv install -r requirements.txt
```

#### 2. Authentication Required
```
[ERROR] No authentication found. Run './start.sh auth' first
```
**Solution**:
```bash
./start.sh auth  # Complete Google login in browser
```

#### 3. Port Already in Use
```
[ERROR] Port 2048 already in use
```
**Solution**:
```bash
./start.sh headless --server-port 8080  # Use different port
```

#### 4. API Not Responding
```bash
./start.sh test  # Check if server is running
```

### Authentication Expiry
Authentication files expire periodically. When this happens:

1. **Delete old authentication**:
   ```bash
   rm auth_profiles/active/*.json
   ```

2. **Re-authenticate**:
   ```bash
   ./start.sh auth
   ```

## Advanced Usage

### Environment Variables
```bash
# Custom proxy settings
export INTERNAL_CAMOUFOX_PROXY="http://proxy:8080"
./start.sh headless

# Debug logging
export DEBUG_LOGS_ENABLED=true
./start.sh debug
```

### Integration with Other Tools

#### Docker
```bash
# Build and run with startup script
docker build -t ai-studio-proxy .
docker run -p 2048:2048 -p 3120:3120 ai-studio-proxy
```

#### Systemd Service
```ini
[Unit]
Description=AI Studio Proxy API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/AIstudioProxyAPI
ExecStart=/path/to/AIstudioProxyAPI/start.sh headless
Restart=always

[Install]
WantedBy=multi-user.target
```

## Script Features

### Automatic Environment Detection
- ✅ Checks virtual environment
- ✅ Validates dependencies  
- ✅ Detects authentication status
- ✅ Auto-configures best mode

### Smart Authentication Handling
- ✅ Auto-moves saved → active auth files
- ✅ Validates authentication before headless mode
- ✅ Provides clear setup instructions

### Comprehensive Testing
- ✅ Health endpoint validation
- ✅ Models endpoint testing
- ✅ API info verification
- ✅ Connection status checks

### User-Friendly Output
- ✅ Colored status messages
- ✅ Clear error descriptions
- ✅ Progress indicators
- ✅ Helpful suggestions

## Support

For issues with the startup scripts:
1. Check the troubleshooting section above
2. Run `./start.sh test` to validate setup
3. Use `./start.sh debug` for interactive debugging
4. Check logs in `logs/app.log`
