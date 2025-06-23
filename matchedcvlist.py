import os
from flask import Flask, request, render_template
from docx import Document
import fitz  # PyMuPDF
import openai
import time
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = 'sk-proj-xxxxxxx'
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
DOCUMENT_FOLDER = "uploads"

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    elif ext == ".pdf":
        doc = fitz.open(file_path)
        return "\n".join([page.get_text() for page in doc])
    return ""

def check_match_with_gpt(text, query):
    prompt = f"""
You are a legal assistant. Does the following document contain content relevant to this search criteria: "{query}"?
If yes, explain briefly why. If not, say "No relevant content found."

Document:
{text}
"""
    for attempt in range(3):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=512
            )
            return response['choices'][0]['message']['content']
        except openai.error.RateLimitError:
            time.sleep(20)  # wait 20 seconds before retrying


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        query = request.form["query"]
        for filename in os.listdir(DOCUMENT_FOLDER):
            filepath = os.path.join(DOCUMENT_FOLDER, filename)
            if os.path.isfile(filepath) and filename.lower().endswith((".docx", ".pdf")):
                text = extract_text(filepath)
                match = check_match_with_gpt(text, query)
                if "No relevant content found" not in match:
                    results.append((filename, match))
    return render_template("matchedcvlist.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)