"""
Backward Compatibility Layer for logging_utils

This module provides backward compatibility for the original logging_utils package.
All functionality is now available through the new aistudio_proxy.utils package.

DEPRECATED: This module is provided for backward compatibility only.
Please update your imports to use: from aistudio_proxy.utils import ...
"""

import warnings
import sys
from pathlib import Path

# Add the new package to the path
sys.path.insert(0, str(Path(__file__).parent))

# Issue deprecation warning
warnings.warn(
    "Importing from 'logging_utils' is deprecated. "
    "Please use 'from aistudio_proxy.utils import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import everything from the new location for backward compatibility
try:
    from aistudio_proxy.utils import *
except ImportError:
    # Fallback to original location if new structure not available
    import sys
    import os
    
    # Add original logging_utils to path
    original_path = os.path.join(os.path.dirname(__file__), 'logging_utils')
    if os.path.exists(original_path):
        sys.path.insert(0, original_path)
        from logging_utils import *
    else:
        raise ImportError(
            "Could not import from either new (aistudio_proxy.utils) or "
            "original (logging_utils) location. Please check your installation."
        )
