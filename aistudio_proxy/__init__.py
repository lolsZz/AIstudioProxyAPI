"""
AIstudio Proxy API - A proxy server for Google AI Studio

This package provides a comprehensive proxy solution for interacting with Google AI Studio
through an OpenAI-compatible API interface.

Main Components:
- api: FastAPI application and routes
- browser: Browser automation using Playwright and Camoufox
- stream: High-performance streaming proxy
- core: Core business logic and data models
- config: Configuration management
- utils: Shared utilities and helpers

Version: 0.6.0-restructured
"""

__version__ = "0.6.0-restructured"
__author__ = "AIstudio Proxy API Team"
__description__ = "A proxy server for Google AI Studio with OpenAI-compatible API"

# Main package imports for convenience
from .core.exceptions import ClientDisconnectedError
from .config.constants import MODEL_NAME, DEFAULT_TEMPERATURE

# Version info
__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "ClientDisconnectedError",
    "MODEL_NAME",
    "DEFAULT_TEMPERATURE"
]
