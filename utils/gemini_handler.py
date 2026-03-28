import os
import json
from google import genai
from google.genai import types

def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=api_key)

def process_health_text(user_input: str) -> dict:
    """
    Calls the Gemini API to extract health insights.
    Validates the structure of the returned JSON.
    """
    client = get_client()
    
    prompt = f"""
    You are a strictly professional medical analysis assistant. Convert the following messy health-related user input into structured actionable insights.
    
    CRITICAL INSTRUCTION: If the input is entirely unrelated to health, medicine, or symptoms (for example: programming, casual chatting, unrelated topics), return empty arrays and set risk_level to 'low', with an action stating 'Input does not appear to be health-related.' Do NOT output health advice for non-health inputs.
    
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
                temperature=0.1,  # Lower temperature for deterministic, efficient logic
                top_p=0.8,
                top_k=40,
                max_output_tokens=500, # Constrained output for efficiency
            )
        )
        
        result = json.loads(response.text)
        
        # Validation of AI Output structure
        expected_keys = {"symptoms", "medical_history", "risk_level", "action"}
        if not expected_keys.issubset(result.keys()):
            raise ValueError("Malformed response from AI model.")
            
        return result
        
    except Exception as e:
        # We re-raise to the caller with a sanitized generic message if we don't want to leak tracebacks
        raise RuntimeError(f"Failed to process with Gemini: {str(e)}")
