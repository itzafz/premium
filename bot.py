import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7663073456:AAER0VSNRmDBpHnzWVXgqpZ-y0zkE_sUf0g"
BACKGROUND_IMAGE = "https://ibb.co/Xfs3f01k"  # use any nice background
FONT_PATH = "arial.ttf"  # change if you have custom font

async def ton_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetch live TON price
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd,inr"
    r = requests.get(url).json()
    usd = r["the-open-network"]["usd"]
    inr = r["the-open-network"]["inr"]

    # Create professional image
    img = Image.open(BACKGROUND_IMAGE).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Fancy large font
    try:
        font_big = ImageFont.truetype(FONT_PATH, 80)
        font_small = ImageFont.truetype(FONT_PATH, 45)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    text1 = f"TON Price"
    text2 = f"USD: ${usd}"
    text3 = f"INR: ₹{inr}"

    # Draw text
    draw.text((50, 50), text1, font=font_big, fill="white")
    draw.text((50, 160), text2, font=font_small, fill="yellow")
    draw.text((50, 230), text3, font=font_small, fill="lightgreen")

    # Save and send
    output = "ton_price_output.png"
    img.save(output)
    await update.message.reply_photo(photo=open(output, "rb"))

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("ton", ton_cmd))
    print("Bot started…")
    app.run_polling()

if __name__ == "__main__":
    main()
