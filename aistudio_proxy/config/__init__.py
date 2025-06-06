"""
Configuration Module - Centralized configuration management

This module provides centralized access to all configuration settings including:
- Application constants and defaults
- Timeout and timing configurations
- CSS selectors for browser automation
- Environment variable handling
- Runtime settings

Backward Compatibility:
All original config/ functionality is preserved and accessible.
"""

# Import all configuration items from various config files
from .constants import *
from .timeouts import *
from .selectors import *
from .settings import *

# Explicitly export main configuration items (for IDE auto-completion and type checking)
__all__ = [
    # Constant configuration
    'MODEL_NAME',
    'CHAT_COMPLETION_ID_PREFIX',
    'DEFAULT_FALLBACK_MODEL_ID',
    'DEFAULT_TEMPERATURE',
    'DEFAULT_MAX_OUTPUT_TOKENS',
    'DEFAULT_TOP_P',
    'DEFAULT_STOP_SEQUENCES',
    'AI_STUDIO_URL_PATTERN',
    'MODELS_ENDPOINT_URL_CONTAINS',
    'USER_INPUT_START_MARKER_SERVER',
    'USER_INPUT_END_MARKER_SERVER',
    'EXCLUDED_MODELS_FILENAME',
    'STREAM_TIMEOUT_LOG_STATE',

    # 超时配置
    'RESPONSE_COMPLETION_TIMEOUT',
    'INITIAL_WAIT_MS_BEFORE_POLLING',
    'POLLING_INTERVAL',
    'POLLING_INTERVAL_STREAM',
    'SILENCE_TIMEOUT_MS',
    'POST_SPINNER_CHECK_DELAY_MS',
    'FINAL_STATE_CHECK_TIMEOUT_MS',
    'POST_COMPLETION_BUFFER',
    'CLEAR_CHAT_VERIFY_TIMEOUT_MS',
    'CLEAR_CHAT_VERIFY_INTERVAL_MS',
    'CLICK_TIMEOUT_MS',
    'CLIPBOARD_READ_TIMEOUT_MS',
    'WAIT_FOR_ELEMENT_TIMEOUT_MS',
    'PSEUDO_STREAM_DELAY',

    # Selector configuration
    'PROMPT_TEXTAREA_SELECTOR',
    'INPUT_SELECTOR',
    'INPUT_SELECTOR2',
    'SUBMIT_BUTTON_SELECTOR',
    'CLEAR_CHAT_BUTTON_SELECTOR',
    'CLEAR_CHAT_CONFIRM_BUTTON_SELECTOR',
    'RESPONSE_CONTAINER_SELECTOR',
    'RESPONSE_TEXT_SELECTOR',
    'LOADING_SPINNER_SELECTOR',
    'OVERLAY_SELECTOR',
    'ERROR_TOAST_SELECTOR',
    'EDIT_MESSAGE_BUTTON_SELECTOR',
    'MESSAGE_TEXTAREA_SELECTOR',
    'FINISH_EDIT_BUTTON_SELECTOR',
    'MORE_OPTIONS_BUTTON_SELECTOR',
    'COPY_MARKDOWN_BUTTON_SELECTOR',
    'COPY_MARKDOWN_BUTTON_SELECTOR_ALT',
    'MAX_OUTPUT_TOKENS_SELECTOR',
    'STOP_SEQUENCE_INPUT_SELECTOR',
    'MAT_CHIP_REMOVE_BUTTON_SELECTOR',
    'TOP_P_INPUT_SELECTOR',
    'TEMPERATURE_INPUT_SELECTOR',

    # 设置配置
    'DEBUG_LOGS_ENABLED',
    'TRACE_LOGS_ENABLED',
    'AUTO_SAVE_AUTH',
    'AUTH_SAVE_TIMEOUT',
    'AUTH_PROFILES_DIR',
    'ACTIVE_AUTH_DIR',
    'SAVED_AUTH_DIR',
    'LOG_DIR',
    'APP_LOG_FILE_PATH',
    'NO_PROXY_ENV',

    # 工具函数
    'get_environment_variable',
    'get_boolean_env',
    'get_int_env',
]
