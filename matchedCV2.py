import os
from flask import Flask, request, render_template
from docx import Document
import fitz  # PyMuPDF
import openai
import time
from dotenv import load_dotenv

load_dotenv()

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
DOCUMENT_FOLDER = "uploads"
# changes
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    elif ext == ".pdf":
        doc = fitz.open(file_path)
        return "\n".join([page.get_text() for page in doc])
    return ""
def build_combined_prompt(file_text_map, query):
    file_sections = []
    for filename, text in file_text_map.items():
        section = f"---\nFilename: {filename}\n{text.strip()}\n"
        file_sections.append(section)

    combined_text = "\n".join(file_sections)
    prompt = f"""
You are a legal assistant. A user is searching for documents relevant to the query: "{query}".

You will be given a list of documents and their contents. For each file, determine if the content is relevant to the query. If yes, explain why. If not, respond with: "No relevant content found."

Documents:
{combined_text}
"""
    return prompt

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        query = request.form["query"]
        file_text_map = {}

        for filename in os.listdir(DOCUMENT_FOLDER):
            filepath = os.path.join(DOCUMENT_FOLDER, filename)
            if os.path.isfile(filepath) and filename.lower().endswith((".docx", ".pdf")):
                text = extract_text(filepath)
                file_text_map[filename] = text

        combined_prompt = build_combined_prompt(file_text_map, query)
        print("Sending combined request to GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": combined_prompt}],
            temperature=0.3,
            max_tokens=4096
        )

        output = response['choices'][0]['message']['content']

        # Optional: rudimentary response splitting by filename
        for filename in file_text_map.keys():
            if filename in output:
                # Extract the section for that file (simple heuristic)
                start = output.find(f"Filename: {filename}")
                if start != -1:
                    end = output.find("Filename:", start + 1)
                    result_text = output[start:end].strip() if end != -1 else output[start:].strip()
                else:
                    result_text = "Unable to parse match result."
                results.append((filename, result_text))
            else:
                results.append((filename, "No relevant content found."))

    return render_template("matchedcvlist.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)