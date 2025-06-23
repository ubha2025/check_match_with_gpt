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


def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You summarize legal documents into concise briefs."},
            {"role": "user", "content": f"Summarize this:\n{text}"}
        ],
        temperature=0.5,
        max_tokens=1024
    )
    return response['choices'][0]['message']['content']


@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            text = extract_text(filepath)
            summary = summarize_text(text)
    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)

