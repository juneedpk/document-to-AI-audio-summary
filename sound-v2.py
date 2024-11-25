from flask import Flask, render_template, request, send_file, make_response
import os
from gtts import gTTS
from PyPDF2 import PdfReader
from docx import Document
import re
from groq import Groq
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)
client = Groq(api_key="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")

# Function to summarize text using Groq API
def summarize_text(input_text):
    try:
        system_prompt = """You are a highly experienced academic admissions consultant with over 10 years of expertise in reviewing and analyzing admission documents for top universities worldwide. Your specialization includes evaluating Statements of Purpose (SOP), Letters of Recommendation (LOR), Personal Statements, and academic correspondence.

Your analysis should include:

1. Document Strength Assessment:
   - Clarity and coherence of narrative
   - Authenticity and personal voice
   - Academic and professional achievements presentation
   - Research alignment and academic goals
   - Writing quality and professionalism

2. Critical Evaluation:
   - Strong points that enhance candidacy
   - Weak areas needing improvement
   - Missing crucial elements
   - Red flags or potential concerns

3. Detailed Recommendations:
   - Specific suggestions for improvement
   - Structure and content organization
   - Language and tone refinement
   - Ways to strengthen impact
   - How to better align with admission requirements

4. Format-Specific Guidelines:
   For SOP:
   - Research interest articulation
   - Academic journey coherence
   - Future goals clarity
   
   For LOR:
   - Specificity of praise
   - Concrete examples
   - Authority of recommender
   
   For Personal Statements:
   - Personal growth demonstration
   - Character development
   - Unique perspectives
   
   For Emails:
   - Professional etiquette
   - Clarity of purpose
   - Follow-up strategy

Please analyze the following document and provide a comprehensive evaluation with actionable improvements for strengthening the application."""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Please provide a detailed analysis and recommendations for the following admission document:\n\n{input_text}"
                }
            ],
            model="llama3-8b-8192",
            temperature=0.4,  # Balanced between creativity and consistency
            max_tokens=3000   # Increased for detailed analysis
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"  # Handle errors gracefully

# Function to convert PDF to text
def pdf_to_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to convert DOCX to text
def docx_to_text(docx_file):
    doc = Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Function to clean extracted text
def clean_text(text):
    # Remove acknowledgements, references, figure captions, labels, table of contents, and special symbols
    text = re.sub(r'(?i)Acknowledgements.*?(\n\n|\Z)', '', text, flags=re.DOTALL)  # Remove Acknowledgements
    text = re.sub(r'(?i)References.*?(\n\n|\Z)', '', text, flags=re.DOTALL)      # Remove References
    text = re.sub(r'(?i)Figure\s+\d+.*?(\n|\Z)', '', text, flags=re.DOTALL)      # Remove Figure captions
    text = re.sub(r'(?i)Table\s+\d+.*?(\n|\Z)', '', text, flags=re.DOTALL)       # Remove Table captions
    text = re.sub(r'(?i)Table of Contents.*?(\n\n|\Z)', '', text, flags=re.DOTALL)  # Remove Table of Contents
    text = re.sub(r'[^\w\s,.!?;:\'-]', '', text)  # Remove special symbols, keeping common punctuation
    return text.strip()

# Function to generate audio using gTTS
def generate_audio_gtts(text, lang='en'):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_file_path = "output_audio.mp3"
    tts.save(audio_file_path)  # Save the audio file
    return "Audio has been generated!", audio_file_path

# Function to create concise audio summaries
def create_audio_summary(detailed_analysis):
    """Create a concise audio summary from the detailed analysis."""
    try:
        system_prompt = """You are an expert at creating concise audio summaries. Your task is to:
1. Condense the detailed analysis into a clear, 2-3 minute speech (approximately 300-400 words)
2. Focus on the most important points and key recommendations
3. Use natural, conversational language suitable for speech
4. Maintain a clear structure: overview, key strengths, main areas for improvement, and vital recommendations
5. Use transition words and phrases that work well in spoken format

Please create a concise audio summary of the following analysis."""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Create a concise audio summary of this analysis:\n\n{detailed_analysis}"
                }
            ],
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=500  # Limit tokens for ~2-3 minute speech
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error creating audio summary: {str(e)}"

def create_analysis_pdf(analysis_text):
    """Create a PDF file with the detailed analysis."""
    pdf = FPDF()
    pdf.add_page()
    
    # Set font for title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Detailed Document Analysis', 0, 1, 'C')
    pdf.ln(10)
    
    # Add timestamp
    pdf.set_font('Arial', 'I', 10)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 10, f'Generated on: {timestamp}', 0, 1, 'R')
    pdf.ln(5)
    
    # Set font for content
    pdf.set_font('Arial', '', 11)
    
    # Split text into lines and add to PDF
    lines = analysis_text.split('\n')
    for line in lines:
        # Handle section headers
        if line.strip().isupper() or line.strip().startswith('#'):
            pdf.set_font('Arial', 'B', 12)
            pdf.ln(5)
            pdf.multi_cell(0, 10, line.strip())
            pdf.set_font('Arial', '', 11)
        else:
            pdf.multi_cell(0, 6, line.strip())
    
    # Save PDF
    pdf_path = "analysis_report.pdf"
    pdf.output(pdf_path)
    return pdf_path

@app.route('/')
def index():
    return render_template('index.html')  # Render the main page

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file:
        # Convert uploaded file to text
        text = pdf_to_text(uploaded_file) if uploaded_file.filename.endswith('.pdf') else docx_to_text(uploaded_file)
        text = clean_text(text)
        
        # Generate detailed analysis
        detailed_analysis = summarize_text(text)
        
        # Create concise audio summary
        audio_summary = create_audio_summary(detailed_analysis)
        
        # Generate audio from the concise summary
        _, audio_file_path = generate_audio_gtts(audio_summary)
        
        # Create PDF
        create_analysis_pdf(detailed_analysis)
        
        return render_template('result.html', audio_file_path='/audio')

@app.route('/download-pdf')
def download_pdf():
    try:
        return send_file('analysis_report.pdf',
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name='analysis_report.pdf')
    except Exception as e:
        return str(e), 404

@app.route('/audio')
def serve_audio():
    try:
        return send_file('output_audio.mp3', mimetype='audio/mpeg')
    except Exception as e:
        return str(e), 404

if __name__ == '__main__':
    app.run(debug=True)
