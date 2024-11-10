# Използваме базов образ за Python
FROM python:3.9-slim

# Задаваме работна директория в контейнера
WORKDIR /app

# Копираме requirements.txt и инсталираме зависимостите
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копираме останалите файлове в работната директория
COPY . .

# Стартираме приложението
CMD ["python", "app.py"]
