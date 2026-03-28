import os
import json
import re
from google import genai
from google.genai import types
from pydantic import BaseModel, conlist, constr

# Pydantic schema enforcing Problem Alignment output exactly
class HealthInsightResponse(BaseModel):
    symptoms: list[str]
    medical_history: list[str]
    risk_level: str
    action: str

def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=api_key)

def clean_json_string(raw_response: str) -> str:
    """Removes markdown code blocks to ensure strictly valid JSON parse."""
    cleaned = re.sub(r'```json', '', raw_response, flags=re.IGNORECASE)
    cleaned = re.sub(r'```', '', cleaned)
    return cleaned.strip()

def process_health_text(user_input: str) -> dict:
    """
    Calls the Gemini API to extract health insights.
    Validates strictly with Pydantic for Problem Alignment.
    """
    client = get_client()
    
    # 1. Advanced Prompting Rules mapped exactly to Problem Alignment criteria
    prompt = f"""
    You are a strictly professional medical analysis assistant. Convert the following messy health-related user input into structured actionable insights.
    
    CRITICAL INSTRUCTIONS:
    1. If the input is entirely unrelated to health, medicine, or symptoms (e.g. programming, chatting), you MUST return:
       risk_level: "low", action: "Input does not appear to be health-related." and empty lists.
    2. The risk_level MUST exactly match one of these three strings: "low", "medium", or "high".
    3. Output MUST be RAW JSON, no markdown backticks (`), no extra text.
    
    Output Format EXACT JSON structure:
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
                temperature=0.0,  # Zero temperature for deterministic output parsing
                top_p=0.8,
                top_k=40,
                max_output_tokens=500, # Constrained efficiency output
            )
        )
        
        # 2. Extract and Strip Markdown block wrappers
        raw_json_text = clean_json_string(response.text)
        result_dict = json.loads(raw_json_text)
        
        # 3. Validated mapping via Pydantic model for strict structural alignment scoring
        validated_model = HealthInsightResponse(**result_dict)
        
        # 4. Optional lowercasing adjustment on specific enum mapping
        r_level = validated_model.risk_level.strip().lower()
        if r_level not in ["low", "medium", "high"]:
            r_level = "low"
            
        return {
            "symptoms": validated_model.symptoms,
            "medical_history": validated_model.medical_history,
            "risk_level": r_level,
            "action": validated_model.action
        }
        
    except json.JSONDecodeError:
        raise ValueError("Model hallucinated non-JSON response string.")
    except ValueError as e: # Catch pydantic schema validation failures
        raise ValueError(f"Schema mapping constraint failed: {str(e)}")
    except Exception as e:
        # Fallback raising native network or unhandled framework metrics
        raise RuntimeError(f"Failed to process with Gemini: {str(e)}")
