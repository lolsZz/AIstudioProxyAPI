#!/usr/bin/env python3
"""
AIstudio Proxy API - Main Entry Point

This module provides the main entry point for the AIstudio Proxy API application.
It maintains compatibility with the original server.py while providing a clean
package-based structure.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path for backward compatibility
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for the AIstudio Proxy API"""
    try:
        # Import the original server module for now to maintain compatibility
        # This will be gradually refactored to use the new package structure
        from server import app
        
        # Set up basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger = logging.getLogger("aistudio_proxy.main")
        logger.info("Starting AIstudio Proxy API via new package structure")
        logger.info(f"Project root: {project_root}")
        
        # For now, we'll use the original server.py logic
        # This maintains full backward compatibility while we transition
        if __name__ == "__main__":
            import uvicorn
            port = int(os.environ.get("PORT", 8000))
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=port,
                log_level="info",
                access_log=False
            )
            
    except ImportError as e:
        print(f"Error importing server module: {e}", file=sys.stderr)
        print("Make sure you're running from the project root directory", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error starting AIstudio Proxy API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
