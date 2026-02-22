import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "7663073456:AAGKttb2SAxgKozbEcit8a3xzBlkmu4Ua3U"

# 🔽 YAHAN APNI IMAGE KA DIRECT LINK DALO (PNG/JPG)
CUSTOM_IMAGE_URL = "https://sacred-beige-wylsnp2rgo.edgeone.app/file_00000000409871fa8cd698965f3507a1.png"  # <-- yahin change karo

def get_ton_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"
    data = requests.get(url, timeout=15).json()
    return data["the-open-network"]["usd"]

def download_image(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert("RGBA")

async def ton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_ton_price()

    # Black background
    canvas = Image.new("RGBA", (1024, 512), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)

    # Load your custom image from URL
    try:
        logo = download_image(CUSTOM_IMAGE_URL)
        logo = logo.resize((200, 200))
        canvas.paste(logo, (760, 40), logo)  # right side watermark
    except Exception as e:
        print("Image load failed:", e)

    # Text (safe default font)
    font = ImageFont.load_default()
    draw.text((40, 40), "TON Live Price", fill=(255, 255, 255), font=font)
    draw.text((40, 140), f"${price}", fill=(255, 255, 255), font=font)

    out_path = "ton_black.png"
    canvas.save(out_path)

    await update.message.reply_photo(photo=open(out_path, "rb"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("ton", ton))

print("Bot running...")
app.run_polling()
