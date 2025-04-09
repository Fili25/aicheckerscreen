FROM python:3.11-slim

# Установка зависимостей
RUN apt-get update &&     apt-get install -y tesseract-ocr &&     apt-get clean &&     rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY . .

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
