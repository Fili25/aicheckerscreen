from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import requests
import shutil
import os
import base64
import re

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

GOOGLE_VISION_API_KEY = "AIzaSyCEN5i2YvLgdgWZu2g0k1EOc65Pb-6jNQ8"
VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"

def recognize_text_google_vision(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    headers = {"Content-Type": "application/json"}
    data = {
        "requests": [{
            "image": {"content": encoded_image},
            "features": [{"type": "TEXT_DETECTION"}]
        }]
    }

    response = requests.post(VISION_API_URL, headers=headers, json=data)
    result = response.json()

    try:
        full_text = result["responses"][0]["fullTextAnnotation"]["text"]
        return full_text
    except Exception:
        return ""

@app.get("/", response_class=HTMLResponse)
async def index():
    return (BASE_DIR / "index.html").read_text(encoding="utf-8")

@app.post("/check")
async def check_image(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = recognize_text_google_vision(file_path)

    is_mytopapps = "mytopapps" in text.lower()

    has_open = (
        "откр" in text.lower() or
        "otkp" in text.lower() or
        re.search(r"[оo0][тtт][кk][рp][ыyиie][тt][ьb6бв]?", text.lower()) is not None
    )

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
