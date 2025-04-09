from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import Image
import pytesseract
import shutil
import os

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>MyTopApps Pinned Check</title>
</head>
<body>
    <h2>Проверка закрепления MyTopApps 🤖</h2>
    <form action='/check' method='post' enctype='multipart/form-data'>
        <input type='file' name='file' accept='image/*' required>
        <button type='submit'>Загрузить и проверить</button>
    </form>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_form():
    return HTML_CONTENT

@app.post("/check")
async def check_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
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
