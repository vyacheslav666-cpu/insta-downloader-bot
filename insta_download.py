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

# Читаем токен из файла token.txt
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Пример финальных опций
YDL_OPTS = {
    # 1. Ограничиваем видео до 720p (или 480p, если ещё меньше)
    "format": "bestvideo[height<=720]+bestaudio/best",
    # 2. Шаблон сохранения
    "outtmpl": "downloads/%(id)s.%(ext)s",
    # 3. Гарантируем mp4-контейнер
    "merge_output_format": "mp4",
    # 4. Загрузка фрагментов (частей видео) в 4 потока параллельно
    "concurrent_fragment_downloads": 4,
    # 5. Предпочитать нативный HLS (быстрее обход FFmpeg для TS)
    "hls_prefer_native": True,
    "hls_use_mpegts": True,
    # 6. Меньше API-запросов к YouTube — используем Android-клиент
    "extractor_args": {
        "youtube": {"player_client": "android"}
    },
    # 7. Добавляем куки только если нужны (для Instagram)
    **({"cookiefile": "cookies.txt"} if os.path.isfile("cookies.txt") else {}),

 # 1) НЕ скачивать плейлисты, только одиночные видео
    "noplaylist": True,

    # 2) (повторим для скорости) ограничиваем 720p, параллельные фрагменты
    "format": "bestvideo[height<=720]+bestaudio/best",
    "concurrent_fragment_downloads": 4,

    # 3) (по желанию) прямо «берём» mp4 без лишнего HLS-TS
    "hls_prefer_native": True,
    "hls_use_mpegts": True,

}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне ссылку на видео из Instagram, YouTube, TikTok или другой поддерживаемый сайт командой\n"
        "/download <URL>\n"
        "и я постараюсь его скачать и отправить тебе."
    )

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /download <URL на видео>")
        return

    url = context.args[0]
    os.makedirs("downloads", exist_ok=True)
    msg = await update.message.reply_text("Скачиваю… ⏳")

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(YDL_OPTS).extract_info(url, download=True)
        )
        filename = yt_dlp.YoutubeDL(YDL_OPTS).prepare_filename(info)

        filesize = os.path.getsize(filename)
        with open(filename, "rb") as video:
            if filesize > 50 * 1024 * 1024:
                await update.message.reply_document(video)
            else:
                await update.message.reply_video(video)

        await msg.edit_text("Готово! 🎉")
        os.remove(filename)
    except Exception as e:
        logging.error("Ошибка при скачивании: %s", e)
        await msg.edit_text(f"Не удалось скачать видео:\n{e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download_media))

    app.run_polling()

if __name__ == "__main__":
    main()

