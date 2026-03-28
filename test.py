from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyAqNReRlDh7Wh7vsKwAVzoeL1sTUZcc9Wc")
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='test',
    )
    print("SUCCESS", response.text)
except Exception as e:
    print("ERROR", e)
