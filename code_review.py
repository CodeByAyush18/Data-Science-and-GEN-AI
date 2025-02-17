import google.generativeai as genai
import os

# Set API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDCjk_rfU-IFTd7rCTdT4syYjtUA4f78Vo"  # Replace with your actual key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to review code using Gemini AI
def review_code(code):
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    prompt = f"Analyze this Python code,if the code is correct do not give any review feedback and if the code is wrong then suggest the bug report and improvements:\n\n{code}"
    
    response = model.generate_content(prompt)
    
    return response.text  # Extract and return the reviewed code feedback
