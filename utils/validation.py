import re
import bleach
from typing import Tuple

def validate_and_sanitize_input(user_input: str) -> Tuple[bool, str, str]:
    """
    Validates and sanitizes raw user input containing potential health symptoms.
    
    This function performs rigorous enterprise-grade validation:
    1. Checks if the input is empty or just whitespace.
    2. Enforces lower/upper character bounds (5 to 1000) to prevent abuse.
    3. Aggressively mitigates Cross-Site Scripting (XSS) via HTML tag bleaching.
    
    Args:
        user_input (str): The raw string provided by the user via the frontend API.
        
    Returns:
        Tuple[bool, str, str]: A tuple composed of:
            - is_valid (bool): True if the input passes boundary checks.
            - sanitized_input (str): The bleached and trimmed string.
            - error_message (str): A descriptive error if validation fails, else empty.
    """
    if not user_input or not isinstance(user_input, str):
        return False, "", "Input must be a non-empty string."

    sanitized = bleach.clean(user_input.strip())
    
    if not sanitized:
        return False, "", "Input cannot be empty after sanitization."
        
    if len(sanitized) < 5:
        return False, "", "Please provide a slightly more descriptive symptom (minimum 5 characters)."
        
    if len(sanitized) > 1000:
        return False, "", "Input is too long. Please keep descriptions under 1000 characters."
        
    return True, sanitized, ""
