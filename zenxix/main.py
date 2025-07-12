# main.py
from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

# Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "deepseek/deepseek-r1:free"

# Store conversation history
conversation_history = []

def query_deepseek(prompt):
    """Send prompt to DeepSeek via OpenRouter API"""
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Zenxix AI Chat"
    }
    
    # Include previous messages in context
    messages = [{"role": "user", "content": prompt}]
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,  # Using json parameter instead of data
            timeout=30
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
        
    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try:
            error_response = response.json()
            error_details = f" | API Error: {error_response.get('error', {}).get('message', 'No details')}"
        except:
            error_details = f" | Status Code: {response.status_code}"
        return f"🚨 HTTP Error: {str(http_err)}{error_details}"
        
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def chat():
    error = None
    
    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        
        if user_message:
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_message})
            
            # Get AI response
            ai_response = query_deepseek(user_message)
            
            # Add AI response to history
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Check for errors
            if "Error" in ai_response or "🚨" in ai_response or "⚠️" in ai_response:
                error = ai_response
    
    return render_template(
        "index.html",
        conversation=conversation_history,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)