#!/usr/bin/env python3
"""
Tez Kino Bot - Video Downloader
Instagram, YouTube, TikTok videolarini yuklab beradi
"""

import os
import logging
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import aiohttp
import json

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token - @BotFather dan oling
BOT_TOKEN = "8792524568:AAHJ0fLRJoAuTdG9g8_LB8TE9sCMXh1E1aU"

# Mini-app URL
WEBAPP_URL = "https://xurram23.github.io/Tez-kino-bot/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot boshlanganda"""
    keyboard = [
        [KeyboardButton("📥 Video Yuklash", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🎬 *Tez Kino Bot* ga xush kelibsiz!

"
        "Instagram, YouTube va TikTok videolarini tez va oson yuklab oling.

"
        "📥 Video Yuklash tugmasini bosing yoki video linkini yuboring!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """WebApp dan kelgan ma'lumotlarni qayta ishlash"""
    try:
        data = update.message.web_app_data.data
        logger.info(f"WebApp data received: {data}")

        data_obj = json.loads(data)
        url = data_obj.get('url', '')
        platform = data_obj.get('platform', '')

        if not url:
            await update.message.reply_text("❌ URL topilmadi!")
            return

        await update.message.reply_text(f"📥 Yuklanmoqda...

Platforma: {platform}
URL: {url}")

        # Video yuklab olish
        video_path = await download_video(url, platform)

        if video_path:
            await update.message.reply_video(video_path, caption="✅ Mana videongiz!")
            # Faylni o'chirish
            if os.path.exists(video_path):
                os.remove(video_path)
        else:
            await update.message.reply_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'g'ridan URL qabul qilish"""
    url = update.message.text.strip()

    # Platformani aniqlash
    if "instagram.com" in url:
        platform = "Instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        platform = "YouTube"
    elif "tiktok.com" in url:
        platform = "TikTok"
    else:
        await update.message.reply_text("❌ Iltimos, Instagram, YouTube yoki TikTok linki yuboring!")
        return

    await update.message.reply_text(f"📥 {platform} dan video yuklanmoqda...")

    video_path = await download_video(url, platform.lower())

    if video_path:
        await update.message.reply_video(video_path, caption="✅ Mana videongiz!")
        if os.path.exists(video_path):
            os.remove(video_path)
    else:
        await update.message.reply_text("❌ Video yuklab bo'lmadi. Linkni tekshiring.")

async def download_video(url: str, platform: str) -> str:
    """Video yuklab olish"""
    try:
        # yt-dlp ni ishlatish (YouTube uchun)
        if platform == "youtube":
            import yt_dlp

            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.%(ext)s',
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return filename

        # Instagram/TikTok uchun (simple approach)
        else:
            return None

    except Exception as e:
        logger.error(f"Download error: {e}")
        return None

def main():
    """Botni ishga tushirish"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.WebAppData(), handle_webapp_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    # Polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
