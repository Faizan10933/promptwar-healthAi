import bleach

def validate_and_sanitize_input(text: str) -> tuple[bool, str, str]:
    """
    Validates and sanitizes user input to prevent XSS and ensure bounds.
    Returns: (is_valid, sanitized_text, error_message)
    """
    if not text or not text.strip():
        return False, "", "Input cannot be empty."
    
    # Restrict length for security and efficiency
    if len(text) > 1000:
        return False, "", "Input exceeds maximum allowed length of 1000 characters."
    
    if len(text) < 5:
        return False, "", "Input is too short to analyze."

    # Sanitize input to prevent basic XSS or HTML injection
    sanitized = bleach.clean(text.strip())
    
    return True, sanitized, ""
