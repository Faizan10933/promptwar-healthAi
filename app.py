import os
import json
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure Gemini API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_input = data.get('text', '')
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
        
    prompt = f"""
    You are a medical analysis assistant. Convert the following messy health-related user input into structured actionable insights.
    
    Output format MUST be EXACTLY this JSON structure:
    {{
      "symptoms": ["list", "of", "symptoms"],
      "medical_history": ["list", "of", "conditions"],
      "risk_level": "low | medium | high",
      "action": "clear suggested action"
    }}
    
    User Input: "{user_input}"
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
                top_p=0.8,
                top_k=40,
                max_output_tokens=1024,
            )
        )
        result = json.loads(response.text)
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
