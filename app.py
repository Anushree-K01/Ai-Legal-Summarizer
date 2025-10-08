import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai

# Import your text extraction functions
from utils import extract_text_from_pdf, extract_text_from_docx

# Load environment variables from .env file
load_dotenv()
# Configure the Gemini API key
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except AttributeError:
    print("⚠️ Error: The GEMINI_API_KEY is missing. Please ensure it is set in your .env file.")
    exit()


app = Flask(__name__)

# Define the path for file uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def home():
    """Landing page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


@app.route('/upload')
def upload():
    """Upload page (function name corrected to 'upload')"""
    return render_template('upload.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    """Handle text or file upload and generate summary"""
    try:
        # Get form data
        file = request.files.get('file')
        text_input = request.form.get('text')
        summary_type = request.form.get('summary_type', 'short')
        language = request.form.get('language', 'English')

        # Validate that we have some content to summarize
        if not file and not text_input:
            return render_template('result.html', summary="⚠️ Please upload a file or enter some text.")

        content = ""

        # --- PROCESS FILE ---
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Extract text based on file type using functions from utils.py
            if filename.lower().endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif filename.lower().endswith('.pdf'):
                content = extract_text_from_pdf(filepath)
            elif filename.lower().endswith('.docx'):
                content = extract_text_from_docx(filepath)
            else:
                return render_template('result.html', summary="⚠️ Unsupported file type. Please upload a .txt, .pdf, or .docx file.")
        
        # --- PROCESS TEXT INPUT ---
        else:
            content = text_input

        # Check if content extraction was successful
        if not content.strip():
            return render_template('result.html', summary="❌ Error: Could not extract any text from the document or the text area was empty.")

        # --- GENERATE SUMMARY ---
        summary_style = "a simple, easy-to-understand summary suitable for a citizen"
        if summary_type == 'detailed':
            summary_style = "a detailed, legally precise summary suitable for a lawyer, including key arguments, precedents, and legal reasoning"

        prompt = (
            f"You are an expert legal analyst. Please summarize the following legal document. "
            f"Create {summary_style}. "
            f"The response must be in {language}.\n\n"
            f"--- Document Content ---\n{content}"
        )

        # Generate summary using the stable 'gemini-pro' model
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        response = model.generate_content(prompt)
        
        summary = response.text if hasattr(response, "text") else "Could not generate a summary."

        return render_template('result.html', summary=summary)

    except Exception as e:
        # Provide a more user-friendly error message
        return render_template('result.html', summary=f"❌ An unexpected error occurred: {str(e)}")


# -------------------------------
# MAIN APP ENTRY
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)