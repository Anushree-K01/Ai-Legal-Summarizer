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
    """Upload page"""
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

        if not file and not text_input:
            return render_template('result.html', summary="⚠️ Please upload a file or enter some text.")

        content = ""

        # --- PROCESS FILE ---
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

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

        if not content.strip():
            return render_template('result.html', summary="❌ Error: Could not extract any text from the document or the text area was empty.")

        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # Step 1: Classify the document
        classification_prompt = (
            "Analyze the following text and determine if it is a 'Legal Document' or a 'General Document'. "
            "Respond with only the words 'Legal Document' or 'General Document'.\n\n"
            f"--- Document Content ---\n{content}"
        )
        classification_response = model.generate_content(classification_prompt)
        document_type = classification_response.parts[0].text.strip()

        # Step 2: Create a context-aware prompt for the summary.
        if summary_type == 'detailed':
            summary_style = (
                "a detailed, legally precise summary suitable for a lawyer. Use markdown bolding (e.g., **text**) to highlight key legal terms, party names, and crucial dates. "
                "If the document pertains to India, ensure all legal interpretations use the Indian legal framework. "
                "After the main summary paragraph, create a section for key highlights with 3-4 bullet points covering the core legal arguments and the final ruling. "
                "Finally, create a separate section for key legal sections and constitutional articles identified. For each one, provide its number and a brief explanation of how it applies to this particular case."
            )
        else: # This is for the 'short' citizen summary
             summary_style = (
                "a simple, easy-to-understand summary paragraph suitable for a citizen. Use markdown bolding (e.g., **text**) to highlight the main parties involved and the final outcome. "
                "After the main summary paragraph, create a section for key takeaways and list 2-3 of the most important points as bullet points."
             )

        if "Legal Document" in document_type:
            context_instruction = (
                "You are an expert legal analyst. The following is a legal document. "
                f"Create {summary_style}."
            )
        else: # Assumes General Document
            context_instruction = (
                "You are a helpful assistant. The following is a general-purpose document. "
                f"Create {summary_style}."
            )

        summarization_prompt = (
            f"{context_instruction} "
            "Do not provide a separate list of general term definitions. "
            f"CRITICAL INSTRUCTION: Your entire response, including all headings, titles, and content, must be written exclusively in the following language: {language}. "
            "Do not use any English unless it is a proper noun (like a name) from the original document.\n\n"
            f"--- Document Content ---\n{content}"
        )

        summary_response = model.generate_content(summarization_prompt)
        summary = summary_response.text

        return render_template('result.html', summary=summary)

    except Exception as e:
        return render_template('result.html', summary=f"❌ An unexpected error occurred: {str(e)}")


# -------------------------------
# MAIN APP ENTRY
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
