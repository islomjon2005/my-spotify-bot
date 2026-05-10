import asyncio
import httpx
import logging
from aiogram import Bot, Dispatcher, types, executor

# 1. BOT SOZLAMALARI
# Tokeningizni quyidagi qo'shtirnoq ichiga yozing
BOT_TOKEN = "8777140863:AAE0N6n8zrDa_wXLzMuYmQZ7Zj08ihaN5xg"

# Loglarni yoqish (xatolarni ko'rish uchun)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# 2. SPOTIFY LINKIDAN MUSIQA MANZILINI OLISH FUNKSIYASI
async def get_download_link(spotify_url):
    api_url = "https://api.spotmate.online/api/v1/download"
    headers = {
        "Referer": "https://spotmate.online/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # API'ga so'rov yuboramiz
            response = await client.get(f"{api_url}?url={spotify_url}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                # API qaytargan ma'lumotni tekshiramiz
                return data.get("downloadUrl") or data.get("link")
            return None
    except Exception as e:
        logging.error(f"API xatosi: {e}")
        return None

# 3. /START BUYRUG'I UCHUN JAVOB
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Menga Spotify linkini yuboring, men sizga musiqani yuklab beraman. 🎵")

# 4. SPOTIFY LINKLARINI QABUL QILISH
@dp.message_handler(lambda message: 'spotify.com' in message.text)
async def handle_spotify(message: types.Message):
    status_msg = await message.answer("🔍 Qidirilmoqda, iltimos kuting...")
    
    # Linkni funksiyaga yuboramiz
    file_url = await get_download_link(message.text)
    
    if file_url:
        try:
            await status_msg.edit_text("✅ Fayl topildi! Telegramga yuborilmoqda...")
            # Audio faylni yuborish
            await bot.send_audio(
                chat_id=message.chat.id,
                audio=file_url,
                caption="Spotmate orqali tayyorlandi 🎧"
            )
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"❌ Faylni yuborishda xato: {e}")
    else:
        await status_msg.edit_text("❌ Kechirasiz, musiqani yuklab olish imkoniyati bo'lmadi. Saytda cheklov bo'lishi mumkin.")

# 5. BOTNI ISHGA TUSHIRISH
if __name__ == '__main__':
    print("Bot ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
