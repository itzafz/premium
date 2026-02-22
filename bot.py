import os
import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "7663073456:AAGKttb2SAxgKozbEcit8a3xzBlkmu4Ua3U"

def get_ton_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"
    data = requests.get(url, timeout=15).json()
    return data["the-open-network"]["usd"]

async def ton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_ton_price()

    # Red background image
    img = Image.new("RGB", (1024, 512), (220, 20, 60))  # crimson red
    draw = ImageDraw.Draw(img)

    # Safe default font (no font file needed)
    font_title = ImageFont.load_default()
    font_price = ImageFont.load_default()

    # Text positions
    draw.text((40, 40), "TON Live Price", fill=(255, 255, 255), font=font_title)
    draw.text((40, 120), f"${price}", fill=(255, 255, 255), font=font_price)
    draw.text((40, 180), "Source: CoinGecko", fill=(255, 255, 255), font=font_title)

    out_path = "ton_price.png"
    img.save(out_path)

    await update.message.reply_photo(photo=open(out_path, "rb"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("ton", ton))

print("Bot running...")
app.run_polling()
