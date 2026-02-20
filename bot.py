import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

COINS = [
    {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC"},
    {"id": "ethereum", "name": "Ethereum", "symbol": "ETH"},
    {"id": "binancecoin", "name": "BNB", "symbol": "BNB"},
    {"id": "solana", "name": "Solana", "symbol": "SOL"},
    {"id": "ripple", "name": "XRP", "symbol": "XRP"},
    {"id": "dogecoin", "name": "Dogecoin", "symbol": "DOGE"},
    {"id": "cardano", "name": "Cardano", "symbol": "ADA"},
    {"id": "tron", "name": "TRON", "symbol": "TRX"},
]

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

def fetch_prices():
    ids = ",".join([c["id"] for c in COINS])
    params = {"vs_currency": "usd", "ids": ids, "sparkline": "false"}
    r = requests.get(API_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def generate_image(data):
    W, H = 1000, 800
    img = Image.new("RGB", (W, H), (5, 8, 17))
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.load_default()
    font = ImageFont.load_default()

    draw.text((20, 20), "⚡ Crypto Dashboard", fill=(200, 220, 255), font=title_font)

    x, y = 20, 80
    card_w, card_h = 220, 160

    for i, coin in enumerate(data):
        cx = x + (i % 4) * (card_w + 20)
        cy = y + (i // 4) * (card_h + 20)

        draw.rounded_rectangle(
            (cx, cy, cx + card_w, cy + card_h),
            radius=16,
            outline=(56, 189, 248),
            width=2,
            fill=(11, 16, 32),
        )

        name = f"{coin['name']} ({coin['symbol'].upper()})"
        price = f"${coin['current_price']:,}"
        change = f"{coin.get('price_change_percentage_24h', 0):.2f}%"

        draw.text((cx + 12, cy + 12), name, fill=(199, 210, 254), font=font)
        draw.text((cx + 12, cy + 50), price, fill=(168, 85, 247), font=font)
        draw.text((cx + 12, cy + 90), f"24h: {change}", fill=(148, 163, 184), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_prices()
        img = generate_image(data)
        await update.message.reply_photo(photo=img, caption="⚡ Live Crypto Dashboard")
    except Exception as e:
        await update.message.reply_text("⚠️ Image generate nahi ho pa rahi.")
        print(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /prices to get live crypto dashboard image 📸")

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN env variable missing")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prices", prices))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
