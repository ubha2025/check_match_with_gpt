import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from docx import Document
import fitz  # PyMuPDF
import openai
from dotenv import load_dotenv
OPENAI_API_KEY = 'sk-proj-xxx'


load_dotenv()
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    elif ext == ".pdf":
        doc = fitz.open(file_path)
        return "\n".join([page.get_text() for page in doc])
    else:
        return "Unsupported file format."

def search_with_gpt(text, query):
    prompt = f"""
Search the following document for content that matches this search criteria: "{query}".
Return only the relevant sections or paragraphs, and explain why they match.

Document:
{text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024
    )
    return response['choices'][0]['message']['content']

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        file = request.files["file"]
        query = request.form["query"]
        if file and query:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            text = extract_text(filepath)
            result = search_with_gpt(text, query)
    return render_template("cvsearch.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)