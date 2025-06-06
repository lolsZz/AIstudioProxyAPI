"""
Core Module - Business logic and data models

This module contains the core business logic and data models including:
- Chat completion models and data structures
- Custom exceptions
- Logging utilities and WebSocket management
- Core constants and types

Backward Compatibility:
All original models/ functionality is preserved and accessible.
"""

# Chat models
from .chat import (
    FunctionCall,
    ToolCall,
    MessageContentItem,
    Message,
    ChatCompletionRequest
)

# 异常类
from .exceptions import ClientDisconnectedError

# 日志工具类
from .logging import (
    StreamToLogger,
    WebSocketConnectionManager,
    WebSocketLogHandler
)

__all__ = [
    # 聊天模型
    'FunctionCall',
    'ToolCall',
    'MessageContentItem',
    'Message',
    'ChatCompletionRequest',

    # 异常
    'ClientDisconnectedError',

    # 日志工具
    'StreamToLogger',
    'WebSocketConnectionManager',
    'WebSocketLogHandler'
]
