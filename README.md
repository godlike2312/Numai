# NumAI - AI Chat Application

A Flask-based AI chat application using OpenRouter API and Firebase authentication.

## Environment Variables

The application requires the following environment variables to be set:

### Required Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key for accessing AI models

### Optional Environment Variables

- `FIREBASE_SERVICE_ACCOUNT`: JSON string containing Firebase service account credentials (alternative to using a service account file)

## Local Development Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - On Windows (Command Prompt):
     ```
     set OPENROUTER_API_KEY=your_openrouter_api_key
     ```
   - On Windows (PowerShell):
     ```
     $env:OPENROUTER_API_KEY="your_openrouter_api_key"
     ```
   - On macOS/Linux:
     ```
     export OPENROUTER_API_KEY=your_openrouter_api_key
     ```

4. Run the application:
   ```
   python app.py
   ```

## Deployment on Render

To deploy this application on Render:

1. Create a new Web Service on Render
2. Connect your repository
3. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add the required environment variables in the Render dashboard:
   - Go to your Web Service → Environment
   - Add the following environment variables:
     - `OPENROUTER_API_KEY`: Your OpenRouter API key
     - `FIREBASE_SERVICE_ACCOUNT`: Your Firebase service account JSON (if not using a file)

## Security Notes

- Never commit API keys or service account files to your repository
- In production, always use environment variables for sensitive credentials
- The application includes a debug mode that bypasses authentication - ensure this is disabled in production by setting `debug=False`