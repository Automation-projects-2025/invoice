from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import tempfile
import shutil
import os
import subprocess  # ✅ Needed for version check

try:
    from docx import Document
    print("✅ [Startup] 'python-docx' loaded successfully.")
except Exception as e:
    print("❌ [Startup] Failed to load 'python-docx':", e)

app = FastAPI()

# ✅ Optional: Check if Tesseract is available
@app.on_event("startup")
async def check_tesseract_version():
    try:
        version = subprocess.check_output(["tesseract", "-v"]).decode()
        print("🧠 Tesseract version:\n", version)
    except Exception as e:
        print("❌ Tesseract not available:", e)


@app.get("/")
def health_check():
    return {"status": "OCR API is running 🚀"}

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    filename = file.filename.lower()
    print(f"📄 Received file: {filename}")

    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    print(f"📂 Temp file saved to: {temp_path}")

    result = {"text": ""}

    try:
        if filename.endswith(".pdf"):
            print("🔍 Processing as PDF using OCR...")
            pages = convert_from_path(temp_path, dpi=300)
            extracted = ""
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                extracted += f"\n--- Page {i+1} ---\n{text}"
            result["text"] = extracted

        elif filename.endswith(".docx"):
            print("📘 Processing as DOCX using python-docx...")
            doc = Document(temp_path)
            extracted = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            result["text"] = extracted

        else:
            error_msg = f"Unsupported file type: {filename}"
            print("❌", error_msg)
            return JSONResponse(status_code=400, content={"error": error_msg})

        print("✅ Text extraction successful.")
    except Exception as e:
        print("❌ Exception during processing:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        os.remove(temp_path)
        print(f"🧹 Deleted temp file: {temp_path}")

    return result
