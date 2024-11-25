# Document to Audio AI Summary

A web application that converts documents into AI-powered audio summaries. Upload your documents (PDF, DOCX) and get concise audio summaries along with document analysis and valuable suggestions.

## Features

- Document Upload Support (PDF, DOCX)
- AI-Powered Text Summarization
- Text-to-Speech Conversion
- Document Analysis
- Downloadable Audio Summaries
- PDF Report Generation

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS
- **AI/ML**: Groq AI
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **Document Processing**: PyPDF2, python-docx

## Prerequisites

- Python 3.11.7 or higher
- Groq API Key

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd sound2
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory and add:
```
GROQ_API_KEY=your_groq_api_key
```

## Running Locally

1. Start the Flask application:
```bash
python sound-v2.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Deployment

This application is configured for deployment on Render.

1. Fork/push this repository to GitHub
2. Create a new Web Service on Render
3. Link your GitHub repository
4. Add environment variables in Render dashboard:
   - GROQ_API_KEY

## Project Structure

```
sound2/
├── sound-v2.py          # Main Flask application
├── requirements.txt     # Python dependencies
├── templates/          
│   └── index.html      # Main webpage template
├── static/             
│   └── favicon.ico     # Website icon
└── render.yaml         # Render deployment configuration
```

## Contributing

Feel free to open issues and pull requests for any improvements.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

For any queries or suggestions, please open an issue in the repository.
