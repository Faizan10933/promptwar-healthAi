# utils/gcp_services.py
import logging

def setup_gcp_services():
    """
    Initializes advanced Google Cloud Platform services.
    Handles fallbacks gracefully to ensure the app boots locally 
    or in a bare-bones GCP project without crashing.
    """
    services = {
        "logging": None,
        "error_reporting": None,
        "translation": None
    }
    
    # 1. Google Cloud Logging
    try:
        from google.cloud import logging as cloud_logging
        client = cloud_logging.Client()
        client.setup_logging()
        services["logging"] = True
    except Exception as e:
        logging.warning("GCP Logging not enabled, falling back to standard.")

    # 2. Google Cloud Error Reporting
    try:
        from google.cloud import error_reporting
        services["error_reporting"] = error_reporting.Client()
    except Exception as e:
        logging.warning("GCP Error Reporting not initialized.")

    # 3. Google Cloud Translation API (For global accessibility)
    try:
        from google.cloud import translate_v2 as translate
        services["translation"] = translate.Client()
    except Exception as e:
        logging.warning("GCP Translation API not initialized.")
        
    return services

def report_error(error_client, error_msg):
    """Graceful wrapper to report errors to GCP if enabled."""
    if error_client:
        try:
            error_client.report(error_msg)
        except Exception:
            pass # Failsafe
    logging.error(f"GCP Error Reporter -> {error_msg}")

def translate_to_english(translate_client, text: str) -> str:
    """Translates user input to English using GCP Translation API."""
    if translate_client and text:
        try:
            result = translate_client.translate(text, target_language='en')
            return result.get('translatedText', text)
        except Exception:
            return text
    return text
