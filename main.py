from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os
import shutil
import tempfile

app = FastAPI()

@app.post("/extract-text/")
async def extract_text(pdf: UploadFile = File(None), raw_text: str = Form(None)):
    result = {"text": ""}

    if pdf:
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            shutil.copyfileobj(pdf.file, temp_pdf)
            temp_pdf_path = temp_pdf.name

        try:
            pages = convert_from_path(temp_pdf_path, dpi=300)
            extracted = ""
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                extracted += f"\n--- Page {i+1} ---\n{text}"
            result["text"] = extracted
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
        finally:
            os.remove(temp_pdf_path)

    elif raw_text:
        result["text"] = raw_text

    else:
        return JSONResponse(status_code=400, content={"error": "No PDF or raw_text provided."})

    return result
