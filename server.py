"""
AIstudio Proxy API - Main Server Entry Point

This is the main server entry point that maintains backward compatibility
while using the new restructured package architecture.

For new development, consider using the new package structure directly:
- from aistudio_proxy.api import create_app
- from aistudio_proxy.browser import initialize_browser
- from aistudio_proxy.core import ChatCompletionRequest
- etc.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path for compatibility
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import from the new package structure
from aistudio_proxy.server import *
from aistudio_proxy.server import app

# --- Main Guard ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=False
    )
