# NumAI - Powered by DeepSeek R1

NumAI is a web application that integrates with the DeepSeek R1 model via OpenRouter API to provide an AI chat interface.

## Features

- Clean, modern UI with animations powered by GSAP
- Real-time chat interface
- Integration with DeepSeek R1 model through OpenRouter API
- Responsive design for desktop and mobile devices

## Project Structure

```
NumAI/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Styling for the application
│   └── js/
│       └── main.js        # JavaScript for frontend functionality
└── templates/
    └── index.html         # Main HTML template
```

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository or download the source code

2. Navigate to the project directory

```bash
cd path/to/NumAI
```

3. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
```

4. Activate the virtual environment

- On Windows:
```bash
venv\Scripts\activate
```

- On macOS/Linux:
```bash
source venv/bin/activate
```

5. Install the required dependencies

```bash
pip install -r requirements.txt
```

### Configuration

The OpenRouter API key is already configured in the `app.py` file. If you need to use a different API key, update the `API_KEY` variable in `app.py`.

### Running the Application

1. Start the Flask development server

```bash
python app.py
```

2. Open your web browser and navigate to `http://127.0.0.1:5000`

## Usage

1. Type your message in the input field at the bottom of the chat interface
2. Press the "Send" button or hit Enter to send your message
3. Wait for the AI to respond

## Security Note

The API key is currently hardcoded in the `app.py` file. For production use, it's recommended to use environment variables or a secure configuration management system to store sensitive information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [DeepSeek R1 Model](https://deepseek.ai)
- [OpenRouter API](https://openrouter.ai)
- [Flask](https://flask.palletsprojects.com/)
- [GSAP (GreenSock Animation Platform)](https://greensock.com/gsap/)