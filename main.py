from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from PIL import Image
import pytesseract
import shutil
import os

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def index():
    return (BASE_DIR / "index.html").read_text(encoding="utf-8")

@app.post("/check")
async def check_image(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = Image.open(file_path)
    text = pytesseract.image_to_string(image, lang="rus+eng")

    is_mytopapps = "mytopapps" in text.lower()
    has_open = "открыть" in text.lower()
    has_pin = "📌" in text or "📍" in text

    pinned = is_mytopapps and (has_open or has_pin)

    return JSONResponse({
        "pinned": pinned,
        "text_found": text,
        "matched": {
            "mytopapps": is_mytopapps,
            "open": has_open,
            "pin": has_pin
        }
    })
