import asyncio, os, yt_dlp, re, logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# токен читаем из token.txt
with open("token.txt") as f:
    TOKEN = f.read().strip()

logging.basicConfig(level=logging.INFO)

YDL_OPTS = {
    "format": "bestvideo[height<=720]+bestaudio/best",
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "merge_output_format": "mp4",
    "concurrent_fragment_downloads": 4,
    "noplaylist": True,
    # cookiefile по-прежнему добавляем, если нужно:
    **({"cookiefile": "cookies.txt"} if os.path.isfile("cookies.txt") else {}),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Просто кинь мне ссылку на видео из Instagram, YouTube, TikTok…"
    )

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # получаем URL
    if context.args:
        url = context.args[0]
    else:
        text = update.message.text or ""
        m = re.search(r'(https?://\S+)', text)
        if not m:
            return
        url = m.group(1)

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

    # ловим все тексты, содержащие http:// или https://
    url_filter = filters.TEXT & filters.Regex(r'https?://\S+')
    app.add_handler(MessageHandler(url_filter, download_media))

    app.run_polling()

if __name__ == "__main__":
    main()

