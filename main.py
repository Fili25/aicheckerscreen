from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from pathlib import Path
import cv2
import pytesseract
import numpy as np
import shutil
import os

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

TEMPLATE_PATH = BASE_DIR / "pin_template.png"
template = cv2.imread(str(TEMPLATE_PATH), cv2.IMREAD_GRAYSCALE)

@app.get("/", response_class=HTMLResponse)
async def index():
    return (BASE_DIR / "index.html").read_text(encoding="utf-8")

@app.post("/check")
async def check_image(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = cv2.imread(str(file_path))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    data = pytesseract.image_to_data(gray, lang="eng", output_type=pytesseract.Output.DICT)
    pinned = False

    for i, word in enumerate(data["text"]):
        if "mytopapps" in word.lower():
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            pad_x, pad_y = 150, 30
            roi = gray[max(y - pad_y, 0): y + h + pad_y, x + w: x + w + pad_x]

            if roi.size == 0:
                continue

            result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= 0.90)
            pinned = len(list(zip(*loc[::-1]))) > 0
            break

    return JSONResponse({ "pinned": pinned })
