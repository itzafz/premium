import os
import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7663073456:AAGKttb2SAxgKozbEcit8a3xzBlkmu4Ua3U"
BG_PATH = "bg.png"   # user-set background

def get_ton_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd&include_24hr_change=true"
    data = requests.get(url).json()
    price = data["the-open-network"]["usd"]
    change = data["the-open-network"]["usd_24h_change"]
    return price, change

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Use /setbg to set background image\n"
        "Use /ton to get TON price image"
    )

async def setbg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Ab background image bhejo.")

async def save_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive(BG_PATH)
        await update.message.reply_text("✅ Background image set ho gayi!")
    else:
        await update.message.reply_text("❌ Please image bhejo.")

async def ton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(BG_PATH):
        await update.message.reply_text("❌ Pehle /setbg se background set karo.")
        return

    price, change = get_ton_price()

    img = Image.open(BG_PATH).convert("RGBA")
    img = img.resize((1024, 1024))  # size fix

    draw = ImageDraw.Draw(img)
    font_big = ImageFont.truetype("arial.ttf", 80)
    font_small = ImageFont.truetype("arial.ttf", 40)

    draw.rectangle((50, 80, 900, 260), fill=(0, 0, 0, 160))
    draw.text((80, 100), "TON Coin Price", font=font_small, fill=(0, 200, 255))
    draw.text((80, 160), f"${price}", font=font_big, fill=(0, 255, 120))
    draw.text((80, 260), f"24h Change: {change:.2f}%", font=font_small, fill=(255, 255, 255))

    img.save("output.png")
    await update.message.reply_photo(photo=open("output.png", "rb"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setbg", setbg))
app.add_handler(MessageHandler(filters.PHOTO, save_bg))
app.add_handler(CommandHandler("ton", ton))

print("Bot running...")
app.run_polling()
