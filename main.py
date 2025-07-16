import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os

# Configure the API
genai.configure(api_key=os.getenv("GEM_API_ENV"))

# Use the faster model
model = genai.GenerativeModel('gemini-1.5-flash')

# Call with config
response = model.generate_content(
    "Explain photosynthesis in 2-3 sentences.",
    generation_config=GenerationConfig(
        temperature=0.7,
        top_p=1,
        top_k=1,
        max_output_tokens=100,  # Limit output for faster response
        stop_sequences=[]       # Optional: stop early on certain tokens
    )
)

print(response.text)
