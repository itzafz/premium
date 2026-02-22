import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7663073456:AAGKttb2SAxgKozbEcit8a3xzBlkmu4Ua3U"

def get_ton_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd&include_24hr_change=true"
    data = requests.get(url).json()
    price = data["the-open-network"]["usd"]
    change = data["the-open-network"]["usd_24h_change"]
    return price, change

async def ton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price, change = get_ton_price()

    img = Image.open("template.png")
    draw = ImageDraw.Draw(img)

    # Font (agar error aaye to koi .ttf font use kar lena)
    font_big = ImageFont.truetype("arial.ttf", 60)
    font_small = ImageFont.truetype("arial.ttf", 40)

    draw.text((120, 220), f"${price}", font=font_big, fill=(0, 255, 100))
    draw.text((120, 300), f"24h Change: {change:.2f}%", font=font_small, fill=(255, 255, 255))

    img.save("output.png")

    await update.message.reply_photo(photo=open("output.png", "rb"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("ton", ton))

print("Bot running...")
app.run_polling()
