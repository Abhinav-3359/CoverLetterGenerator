from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import google.generativeai as genai
import fitz  #MYPUDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
CORS(app)

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(),filetype="pdf")
    text = ""
    for page in doc:
        text+=page.get_text()
    return text

def generate_cover_letter_prompt(resume_text, job_description):
    prompt = f"""
    You are an expert career assistant. Given the resume and job description, write a powerful 
    cover letter.

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Generate a tailored cover letter:
    """

    model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

    response = model.generate_content(prompt)
    return response.text.strip()

def wrap_text(text, max_chars=90):
    """Wrap text by character count."""
    lines = []
    for line in text.split("\n"):
        while len(line) > max_chars:
            split_index = line.rfind(" ", 0, max_chars)
            if split_index == -1:
                split_index = max_chars
            lines.append(line[:split_index])
            line = line[split_index:].lstrip()
        lines.append(line)
    return lines


def generate_pdf(cover_letter_text):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    x = 1 * inch
    y = height - 1 * inch

    wrapped_lines = wrap_text(cover_letter_text, max_chars=90)

    for line in wrapped_lines:
        p.drawString(x, y, line)
        y -= 14
        if y < 1 * inch:  
            p.showPage()
            y = height - 1 * inch

    p.save()
    buffer.seek(0)
    return buffer

@app.route('/download-pdf', methods=['POST']) 
def generate():
 text = request.json['text']
 pdf_buffer = generate_pdf(text)
 return send_file(pdf_buffer, as_attachment=True, download_name="cover_letter.pdf", mimetype='application/pdf')

@app.route('/generate-cover-letter-text',methods=["POST"])
def generate_text():
    resume_file = request.files['resume']
    job_desc = request.form['job_description']
    resume_text= extract_text_from_pdf(resume_file)
    cover_letter=generate_cover_letter_prompt(resume_text,job_desc)
    return jsonify({'cover_letter': cover_letter})

if __name__ =='__main__':
    app.run(debug=True)
            