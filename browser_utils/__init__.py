# --- browser_utils/__init__.py ---
# Browser operation utilities module
from .initialization import _initialize_page_logic, _close_page_logic, signal_camoufox_shutdown
from .operations import (
    _handle_model_list_response,
    detect_and_extract_page_error,
    save_error_snapshot,
    get_response_via_edit_button,
    get_response_via_copy_button,
    _wait_for_response_completion,
    _get_final_response_content,
    get_raw_text_content
)
from .model_management import (
    switch_ai_studio_model,
    load_excluded_models,
    _handle_initial_model_state_and_storage,
    _set_model_from_page_display
)

__all__ = [
    # Initialization related
    '_initialize_page_logic',
    '_close_page_logic',
    'signal_camoufox_shutdown',

    # Page operation related
    '_handle_model_list_response',
    'detect_and_extract_page_error',
    'save_error_snapshot',
    'get_response_via_edit_button',
    'get_response_via_copy_button',
    '_wait_for_response_completion',
    '_get_final_response_content',
    'get_raw_text_content',

    # Model management related
    'switch_ai_studio_model',
    'load_excluded_models',
    '_handle_initial_model_state_and_storage',
    '_set_model_from_page_display'
]
