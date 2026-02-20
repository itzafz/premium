import os
import io
import math
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN") or "PASTE_YOUR_BOT_TOKEN"

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

COINS = [
    {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC"},
    {"id": "ethereum", "name": "Ethereum", "symbol": "ETH"},
    {"id": "binancecoin", "name": "BNB", "symbol": "BNB"},
    {"id": "solana", "name": "Solana", "symbol": "SOL"},
    {"id": "ripple", "name": "XRP", "symbol": "XRP"},
    {"id": "dogecoin", "name": "Dogecoin", "symbol": "DOGE"},
    {"id": "cardano", "name": "Cardano", "symbol": "ADA"},
    {"id": "tron", "name": "TRON", "symbol": "TRX"},
    {"id": "toncoin", "name": "Toncoin", "symbol": "TON"},
]

# --------- FONTS (thick, bold) ----------
def load_fonts():
    try:
        title = ImageFont.truetype("fonts/Poppins-Bold.ttf", 56)
        price = ImageFont.truetype("fonts/Poppins-Bold.ttf", 42)
        label = ImageFont.truetype("fonts/Poppins-Bold.ttf", 24)
        small = ImageFont.truetype("fonts/Poppins-Bold.ttf", 20)
    except:
        title = ImageFont.load_default()
        price = ImageFont.load_default()
        label = ImageFont.load_default()
        small = ImageFont.load_default()
    return title, price, label, small

TITLE_FONT, PRICE_FONT, LABEL_FONT, SMALL_FONT = load_fonts()

# --------- FETCH PRICES (TON FIXED) ----------
def fetch_prices():
    ids = ",".join([c["id"] for c in COINS])
    r = requests.get(API_URL, params={"vs_currency": "usd", "ids": ids, "sparkline": "false"}, timeout=15)
    r.raise_for_status()
    data = r.json()

    if not any(c.get("id") == "toncoin" for c in data):
        r2 = requests.get(API_URL, params={"vs_currency": "usd", "ids": "toncoin", "sparkline": "false"}, timeout=15)
        r2.raise_for_status()
        extra = r2.json()
        if extra:
            data.extend(extra)

    order = {c["id"]: i for i, c in enumerate(COINS)}
    data.sort(key=lambda x: order.get(x.get("id"), 999))
    return data

# --------- IMAGE GENERATOR ----------
def generate_image(data):
    W, H = 1280, 720  # 16:9
    img = Image.new("RGB", (W, H), "#050811")
    draw = ImageDraw.Draw(img)

    # background glow
    glow = Image.new("RGB", (W, H), "#050811")
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse(( -200, -200, 600, 400), fill="#1e40af")
    gdraw.ellipse(( 700, -150, 1400, 450), fill="#6d28d9")
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    img = Image.blend(img, glow, 0.45)
    draw = ImageDraw.Draw(img)

    draw.text((40, 20), "⚡ CRYPTO DASHBOARD", font=TITLE_FONT, fill="#cfe9ff")

    cols = 3
    card_w = (W - 80) // cols
    card_h = 150
    x0, y0 = 40, 110

    for i, coin in enumerate(data):
        col = i % cols
        row = i // cols
        x = x0 + col * card_w
        y = y0 + row * (card_h + 20)

        # card bg
        draw.rounded_rectangle((x, y, x + card_w - 20, y + card_h), radius=24, fill="#0b1020", outline="#38bdf8", width=2)

        # logo
        try:
            logo = Image.open(requests.get(coin["image"], stream=True).raw).convert("RGBA")
            logo = logo.resize((48, 48))
            img.paste(logo, (x + 16, y + 16), logo)
        except:
            pass

        name = f'{coin["name"]} ({coin["symbol"].upper()})'
        price = f'${coin["current_price"]:,.2f}'
        change = coin.get("price_change_percentage_24h") or 0
        vol = coin.get("total_volume") or 0

        change_color = "#22c55e" if change >= 0 else "#ef4444"
        change_txt = f'{change:+.2f}%'
        vol_txt = f'Vol 24h: ${vol/1e9:.2f}B'

        draw.text((x + 80, y + 18), name, font=LABEL_FONT, fill="#e5e7eb")
        draw.text((x + 80, y + 52), price, font=PRICE_FONT, fill="#a78bfa")
        draw.text((x + 80, y + 100), change_txt, font=LABEL_FONT, fill=change_color)
        draw.text((x + card_w - 240, y + 100), vol_txt, font=SMALL_FONT, fill="#94a3b8")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --------- TELEGRAM HANDLER ----------
async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Dashboard bana raha hoon...")
    data = fetch_prices()
    img = generate_image(data)
    await update.message.reply_photo(photo=img, caption="⚡ Live Crypto Prices (16:9, Pro Style)")

# --------- BOT START ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("prices", prices))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
