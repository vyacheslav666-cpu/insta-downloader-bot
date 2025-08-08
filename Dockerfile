FROM python:3.11-slim

# ffmpeg нужен yt-dlp для склейки аудио/видео
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ставим зависимости отдельно — кэш быстрее
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# копируем код
COPY insta_download.py ./

# директорию с загрузками будем монтировать
VOLUME ["/app/downloads"]

# запуск
CMD ["python", "insta_download.py"]

