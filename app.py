from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import json
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key for sessions

# OpenRouter API key
API_KEY = "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"

# Route for the login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route for the register page
@app.route('/register')
def register():
    return render_template('register.html')

# Route for the reset password page
@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')

# Protected home route - redirects to login if not authenticated
# The actual authentication check is handled by Firebase in the frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('message', '')
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        # Call OpenRouter API with DeepSeek model
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://numai.app",  # Replace with your actual site URL
                "X-Title": "NumAI",  # Replace with your actual site name
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are NumAI, a helpful assistant powered by DeepSeek R1. When a user says only 'hello', respond with just 'Hello! How can I help you today?' and nothing more. For all other queries, respond normally with appropriate markdown formatting: **bold text** for titles, backticks for code, and proper code blocks with language specification. You can use emoji shortcodes like :smile:, :thinking:, :idea:, :code:, :warning:, :check:, :star:, :heart:, :info:, and :rocket: in your responses. When providing code examples, make it clear these are standalone examples."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                "response_format": {
                    "type": "text"
                }
            })
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Extract the assistant's message
        assistant_message = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        return jsonify({'response': assistant_message})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)