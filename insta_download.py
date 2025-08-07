import asyncio
import logging
import os
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

TOKEN = "8448892888:AAFcAub3t-wHYeAOYvAgcITe3MFyap_71Wg" 

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли ссылку на видео из Instagram командой /download <URL>, и я его скачиваю."
    )

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /download <URL на пост или рилс>")
        return

    url = context.args[0]
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s"
    }
    os.makedirs("downloads", exist_ok=True)
    msg = await update.message.reply_text("Загружаю… ⏳")

    try:
        # Получаем текущий цикл и запускаем yt-dlp в пуле потоков
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True)
        )
        # Формируем имя файла по тому же ydl_opts
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)

        # Отправляем видео
        with open(filename, "rb") as video:
            await update.message.reply_video(video)
        await msg.edit_text("Готово! 🎉")
    except Exception as e:
        logging.error("Ошибка при скачивании: %s", e)
        await msg.edit_text(f"Не удалось скачать видео:\n{e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download_instagram))

    app.run_polling()

if __name__ == "__main__":
    main()

