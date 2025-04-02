from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import tempfile
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "/tmp/pdf_pages"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "OCR API is healthy ✅"}

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    filename = file.filename
    print(f"📄 Received file: {filename}")

    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    print(f"📂 Temp file saved at: {temp_path}")

    result = {"filename": filename, "text": ""}

    try:
        if filename.lower().endswith(".pdf"):
            print("🔍 Starting PDF to image conversion...")
            try:
                pages = convert_from_path(temp_path, dpi=300)
                print(f"✅ Converted {len(pages)} pages to images")
            except Exception as e:
                print(f"❌ Failed to convert PDF to images: {e}")
                return JSONResponse(status_code=500, content={"error": "PDF to image conversion failed"})

            extracted = ""
            for i, page in enumerate(pages):
                img_path = os.path.join(UPLOAD_DIR, f"page_{i+1}.png")
                page.save(img_path, "PNG")
                print(f"🖼️ Saved page image to {img_path}")

                try:
                    text = pytesseract.image_to_string(page)
                    extracted += f"\n--- Page {i+1} ---\n{text}"
                except Exception as e:
                    print(f"❌ OCR failed on page {i+1}: {e}")
                    extracted += f"\n--- Page {i+1} ---\n[OCR failed]"

            result["text"] = extracted

        elif filename.lower().endswith(".docx"):
            print("📘 Processing DOCX using python-docx...")
            from docx import Document
            doc = Document(temp_path)
            extracted = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            result["text"] = extracted

        else:
            error_msg = f"Unsupported file type: {filename}"
            print("❌", error_msg)
            return JSONResponse(status_code=400, content={"error": error_msg})

        print("✅ Text extraction complete")
    except Exception as e:
        print("❌ Unexpected error:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        os.remove(temp_path)
        print(f"🧹 Deleted temp file: {temp_path}")

    return result
