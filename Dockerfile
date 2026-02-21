# Python 3.11 base image
FROM python:3.11-slim

# Ishchi papka
WORKDIR /app

# Requirements nusxa olish
COPY requirements.txt .

# Pip yangilash va kutubxonalarni o‘rnatish
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Loyihani ko‘chirish
COPY . .

# Botni ishga tushirish
CMD ["python", "main.py"]
