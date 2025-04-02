from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path
from docx import Document
from PIL import Image
import pytesseract
import tempfile
import shutil
import os

app = FastAPI()

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    filename = file.filename.lower()
    result = {"text": ""}

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        if filename.endswith(".pdf"):
            pages = convert_from_path(temp_path, dpi=300)
            extracted = ""
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                extracted += f"\n--- Page {i+1} ---\n{text}"
            result["text"] = extracted

        elif filename.endswith(".docx"):
            doc = Document(temp_path)
            extracted = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            result["text"] = extracted

        else:
            return JSONResponse(status_code=400, content={"error": "Unsupported file type. Upload PDF or DOCX only."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        os.remove(temp_path)

    return result
