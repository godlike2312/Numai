from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import json
import os
import secrets
import time
import traceback
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key for sessions

# Initialize Firebase Admin SDK
# Use the service account file for authentication
try:
    # First try the service account file in the static/js folder
    cred = credentials.Certificate('static/js/bot-ai-ind-firebase-adminsdk-fbsvc-108e169d30.json')
    firebase_admin.initialize_app(cred)
except ValueError:
    # App already initialized
    pass
except FileNotFoundError:
    # Try the service account file in the root directory
    try:
        cred = credentials.Certificate('firebase-service-account.json')
        firebase_admin.initialize_app(cred)
    except FileNotFoundError:
        print("Firebase service account files not found. Using application default credentials.")
        try:
            firebase_admin.initialize_app()
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK: {str(e)}")
            # Continue without Firebase Admin SDK
            pass

# OpenRouter API key
API_KEY = "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"

# Define available models with fallbacks
AVAILABLE_MODELS = [
    "deepseek/deepseek-r1-0528:free",  # Primary model
    "mistralai/mistral-7b-instruct:free",  # First fallback
    "google/gemma-7b-it:free",  # Second fallback
    "meta-llama/llama-3-8b-instruct:free"  # Third fallback
]

# Helper function to get OpenRouter headers
def get_openrouter_headers(request_obj=None, additional_headers=None):
    """Generate consistent headers for OpenRouter API requests"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Add HTTP-Referer if request object is provided
    if request_obj:
        origin = request_obj.headers.get('Origin')
        referer = request_obj.headers.get('Referer')
        headers["HTTP-Referer"] = origin or referer or "https://numai.onrender.com"
        headers["X-Title"] = "NumAI"
    
    # Add any additional headers
    if additional_headers:
        headers.update(additional_headers)
    
    return headers

# Helper function to verify Firebase ID token
def verify_firebase_token(request_obj):
    """Verify Firebase ID token from Authorization header"""
    # Get the Authorization header
    auth_header = request_obj.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    # Extract the token
    token = auth_header.split('Bearer ')[1]
    
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        # For development/testing purposes, you can bypass token verification
        # This should be removed in production
        if app.debug:
            print("WARNING: Running in debug mode. Bypassing token verification.")
            # Create a mock decoded token with a user ID
            return {"uid": "test-user-id"}
        return None

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

# Route for the system status page
@app.route('/status')
def status():
    return render_template('status.html')

# Protected home route - redirects to login if not authenticated
# The actual authentication check is handled by Firebase in the frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Log request headers for debugging
        print(f"Request headers: {dict(request.headers)}")
        
        # Verify Firebase token
        decoded_token = verify_firebase_token(request)
        if not decoded_token:
            return jsonify({'error': 'Unauthorized. Please log in.'}), 401
        
        # Get user ID from token
        user_id = decoded_token.get('uid')
        print(f"Authenticated user: {user_id}")
        
        user_input = request.json.get('message', '')
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        # First check the API key status
        try:
            key_status_response = requests.get(
                url="https://openrouter.ai/api/v1/auth/key",
                headers=get_openrouter_headers(request)
            )
            
            if key_status_response.status_code != 200:
                return jsonify({'error': f'API key validation failed: {key_status_response.text}'}), 401
                
            key_status = key_status_response.json()
            # Log the key status for debugging
            print(f"API Key Status: {json.dumps(key_status, indent=2)}")
            
            # Check if we have enough credits
            if key_status.get('rate_limits'):
                for limit in key_status.get('rate_limits', []):
                    if limit.get('remaining', 0) <= 0:
                        return jsonify({'error': f"Rate limit reached: {limit.get('limit_type')}. Please try again later."}), 429
        except Exception as key_error:
            print(f"Error checking API key status: {str(key_error)}")
            # Continue with the request even if key status check fails
        
        # Try each model in order until one works
        last_error = None
        for model_index, model in enumerate(AVAILABLE_MODELS):
            try:
                print(f"Trying model: {model} ({model_index + 1}/{len(AVAILABLE_MODELS)})")
                
                # Call OpenRouter API with the current model
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers=get_openrouter_headers(request),
                    data=json.dumps({
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are NumAI, a helpful assistant . When a user says only 'hello', respond with just 'Hello! How can I help you today?' and nothing more. For all other queries, respond normally with appropriate markdown formatting: **bold text** for titles, backticks for code, and proper code blocks with language specification. You can use emoji shortcodes like :smile:, :thinking:, :idea:, :code:, :warning:, :check:, :star:, :heart:, :info:, and :rocket: in your responses. When providing code examples, make it clear these are standalone examples."
                            },
                            {
                                "role": "user",
                                "content": user_input
                            }
                        ],
                        "response_format": {
                            "type": "text"
                        }
                    }),
                    timeout=30  # Shorter timeout for faster fallback
                )
                
                # Check if the request was successful
                response.raise_for_status()
                
                # Parse the response
                result = response.json()
                
                # Extract the assistant's message
                assistant_message = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                if not assistant_message:
                    print(f"Empty response from model: {model}")
                    continue  # Try the next model
                
                # If we got here, we have a successful response
                print(f"Successfully got response from model: {model}")
                return jsonify({
                    'response': assistant_message,
                    'model_used': model  # Include which model was used for debugging
                })
                
            except (requests.exceptions.RequestException, Exception) as e:
                print(f"Error with model {model}: {str(e)}")
                last_error = e
                
                # Add a small delay before trying the next model to avoid rate limiting
                if model_index < len(AVAILABLE_MODELS) - 1:  # If not the last model
                    time.sleep(1)  # Wait 1 second before trying the next model
        
        # If we get here, all models failed
        if isinstance(last_error, requests.exceptions.Timeout):
            return jsonify({'error': 'All model requests timed out. Please try again later.'}), 504
        elif isinstance(last_error, requests.exceptions.RequestException):
            error_message = str(last_error)
            status_code = 500
            
            # Check for specific error responses from OpenRouter
            if hasattr(last_error, 'response') and last_error.response:
                try:
                    error_data = last_error.response.json()
                    if 'error' in error_data:
                        error_message = f"OpenRouter API error: {error_data['error']}"
                        
                    # Set appropriate status code
                    if last_error.response.status_code == 429:
                        status_code = 429  # Too Many Requests
                        error_message = "Rate limit exceeded for all models. Please try again later."
                except:
                    pass
            
            print(f"All models failed with API Request Error: {error_message}")
            return jsonify({'error': error_message}), status_code
        else:
            print(f"All models failed with Unexpected Error: {str(last_error)}")
            return jsonify({'error': f'All models failed: {str(last_error)}'}), 500
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Unexpected Error outside model loop: {str(e)}\n{error_details}")
        
        # Provide a more user-friendly error message
        error_message = "We're experiencing technical difficulties with our AI service. Please try again later."
        
        # Include more details in development environment
        if app.debug:
            error_message += f" Error details: {str(e)}"
        
        return jsonify({
            'error': error_message,
            'status': 'error',
            'retry_recommended': True
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Endpoint to check the status of the OpenRouter API and available models"""
    try:
        # Log request headers for debugging
        print(f"Status endpoint headers: {dict(request.headers)}")
        
        # Check API key status
        key_status_response = requests.get(
            url="https://openrouter.ai/api/v1/auth/key",
            headers=get_openrouter_headers(request)
        )
        
        if key_status_response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'API key validation failed: {key_status_response.text}',
                'code': key_status_response.status_code
            }), 401
        
        key_status = key_status_response.json()
        
        # Check models availability
        models_response = requests.get(
            url="https://openrouter.ai/api/v1/models",
            headers=get_openrouter_headers(request)
        )
        
        models_data = models_response.json() if models_response.status_code == 200 else {'error': 'Failed to fetch models'}
        
        # Prepare response with diagnostic information
        available_models = []
        if 'data' in models_data:
            for model in models_data['data']:
                model_id = model.get('id')
                if model_id in AVAILABLE_MODELS:
                    available_models.append({
                        'id': model_id,
                        'name': model.get('name', 'Unknown'),
                        'context_length': model.get('context_length', 0),
                        'pricing': model.get('pricing', {})
                    })
        
        return jsonify({
            'status': 'ok',
            'api_key_status': key_status,
            'configured_models': AVAILABLE_MODELS,
            'available_models': available_models,
            'server_time': time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in API status endpoint: {str(e)}\n{error_details}")
        
        # Provide a more user-friendly error message
        error_message = "Unable to retrieve API status information. Please try again later."
        
        # Include more details in development environment
        if app.debug:
            error_message += f" Error details: {str(e)}"
        
        return jsonify({
            'status': 'error',
            'message': error_message,
            'server_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }), 500

if __name__ == '__main__':
    app.run(debug=True)