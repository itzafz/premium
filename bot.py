import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "7663073456:AAGKttb2SAxgKozbEcit8a3xzBlkmu4Ua3U"

# 🔽 YAHAN APNI FULL BACKGROUND IMAGE KA DIRECT LINK DALO
BG_IMAGE_URL = "https://sacred-beige-wylsnp2rgo.edgeone.app/file_00000000409871fa8cd698965f3507a1.png"  # <-- change this

def get_ton_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"
    data = requests.get(url, timeout=15).json()
    return data["the-open-network"]["usd"]

def download_image(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert("RGBA")

def cover_resize(img, size=(1024, 512)):
    bg_w, bg_h = img.size
    tgt_w, tgt_h = size
    scale = max(tgt_w / bg_w, tgt_h / bg_h)
    new_size = (int(bg_w * scale), int(bg_h * scale))
    img = img.resize(new_size, Image.LANCZOS)
    left = (img.width - tgt_w) // 2
    top = (img.height - tgt_h) // 2
    return img.crop((left, top, left + tgt_w, top + tgt_h))

async def ton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_ton_price()

    # Full background from URL (cover)
    bg = download_image(BG_IMAGE_URL)
    canvas = cover_resize(bg, (1024, 512))

    # Black overlay for readability
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 140))
    canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    # Safe default font (no font file needed)
    font_title = ImageFont.load_default()
    font_price = ImageFont.load_default()

    draw.text((40, 40), "TON Live Price", fill=(255, 255, 255), font=font_title)
    draw.text((40, 140), f"${price}", fill=(255, 255, 255), font=font_price)

    out_path = "ton_full_bg.png"
    canvas.save(out_path)

    await update.message.reply_photo(photo=open(out_path, "rb"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("ton", ton))

print("Bot running...")
app.run_polling()
