# AI Driven Legal Document Summarizer

An intelligent web application that leverages the power of Google's Gemini API to summarize complex legal documents. This tool is designed to help both legal professionals and citizens quickly understand the key points of lengthy legal texts by providing clear, concise summaries in multiple languages.

## ✨ Features

-   **Multiple Input Methods**: Summarize documents by uploading `.txt`, `.pdf`, or `.docx` files, or by directly pasting text.
-   **Customizable Summary Types**: Choose between a **simple summary** (easy for citizens to understand) or a **detailed summary** (for legal professionals).
-   **Multi-language Support**: Generate summaries in a variety of languages, including English, Hindi, Spanish, Kannada, and more.
-   **Web-Based Interface**: A clean and user-friendly interface built with Flask.

---

## 📂 Project Structure

Here is the file and directory structure for the project:

ai-legal-summarizer/
├── app.py              # The main Flask application logic
├── requirements.txt    # A list of all Python dependencies for the project
├── utils.py            # Helper functions for extracting text from PDF/DOCX files
├── .env                # Your secret API key (This file is NOT committed to Git)
├── static/
│   └── css/
│       └── style.css   # All custom CSS styles for the web pages
│   └── js/
│       └── script.js   # JavaScript to make web pages interactive
└── templates/
├── index.html      # The application's home page
├── upload.html     # The page for uploading files and entering text
├── result.html     # The page that displays the final summary
└── dashboard.html  # The dashboard page
