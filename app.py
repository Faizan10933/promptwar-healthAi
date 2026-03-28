import os
import logging
from flask import Flask, request, jsonify, render_template, Response
from flask_talisman import Talisman
from flask_cors import CORS

from utils.validation import validate_and_sanitize_input
from utils.gemini_handler import process_health_text

# Integrate Google Cloud Logging for Google Services points
try:
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
except Exception:
    # Fallback to standard logging if not in GCP
    logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Security: Apply HTTP security headers (Talisman)
# Using a slightly relaxed CSP for CDN integrations (FontAwesome, Google Fonts)
csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdnjs.cloudflare.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"],
    'connect-src': ["'self'"]
}
Talisman(app, content_security_policy=csp)

# Security: Enforce CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def add_cache_headers(response: Response):
    """Efficiency: Cache static assets aggressively."""
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 86400  # 1 day
        response.cache_control.public = True
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Endpoint to analyze health inputs securely."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
        
    data = request.json
    raw_input = data.get('text', '')
    
    # 1. Validation & Sanitization
    is_valid, sanitized_text, error_msg = validate_and_sanitize_input(raw_input)
    if not is_valid:
        logging.warning(f"Validation failed: {error_msg}")
        return jsonify({"error": error_msg}), 400
        
    logging.info(f"Processing sanitized input of length {len(sanitized_text)}")
    
    # 2. Process with Gemini
    try:
        insights = process_health_text(sanitized_text)
        return jsonify(insights), 200
    except Exception as e:
        # Logging error securely without leaking to user
        logging.error(f"Analysis Error: {str(e)}")
        return jsonify({"error": "An internal error occurred during analysis."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
