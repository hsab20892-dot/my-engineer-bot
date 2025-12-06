FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# هذا المنفذ مخصص لـ Hugging Face
ENV PORT=7860

CMD ["python", "bot.py"]
