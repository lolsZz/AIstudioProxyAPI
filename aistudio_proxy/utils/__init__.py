"""
Utils Module - Shared utilities and helpers

This module contains shared utility functions including:
- Logging setup and configuration
- Authentication utilities
- General helper functions
- Validation utilities

Backward Compatibility:
All original logging_utils functionality is preserved and accessible.
"""

# Logging utilities
from .setup import setup_server_logging, restore_original_streams

__all__ = [
    'setup_server_logging',
    'restore_original_streams'
]
