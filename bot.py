import os, io, requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
    {"id": "toncoin", "name": "Toncoin", "symbol": "TON"},
]

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

def fetch_prices():
    ids = ",".join([c["id"] for c in COINS])
    r = requests.get(API_URL, params={"vs_currency": "usd", "ids": ids, "sparkline": "false"}, timeout=15)
    r.raise_for_status()
    return r.json()

def load_font(size, weight="regular"):
    try:
        if weight == "black":
            return ImageFont.truetype("assets/Inter-Black.ttf", size)
        if weight == "bold":
            return ImageFont.truetype("assets/Inter-Bold.ttf", size)
        return ImageFont.truetype("assets/Inter-Regular.ttf", size)
    except:
        return ImageFont.load_default()

def gradient_bg(w, h):
    img = Image.new("RGB", (w, h), "#050811")
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(5 + (56-5) * (y/h))
        g = int(8 + (189-8) * (y/h))
        b = int(17 + (248-17) * (y/h))
        draw.line((0, y, w, y), fill=(r//3, g//3, b//3))
    return img

def neon_card(base, box, glow_color=(56,189,248)):
    glow = Image.new("RGBA", base.size, (0,0,0,0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.rounded_rectangle(box, radius=28, fill=glow_color+(80,))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    base.alpha_composite(glow)

def generate_image(data):
    W, H = 1920, 1080  # 16:9
    bg = gradient_bg(W, H).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    title_font = load_font(68, "black")
    sub_font   = load_font(22, "bold")
    name_font  = load_font(26, "bold")
    price_font = load_font(44, "black")
    meta_font  = load_font(20, "bold")

    draw.text((64, 36), "⚡ Crypto Dashboard", fill=(210,230,255,255), font=title_font)
    draw.text((64, 110), "Live market snapshot • Auto refresh", fill=(150,170,200,255), font=sub_font)

    cols = 3
    pad = 36
    card_w = (W - pad*(cols+1)) // cols
    card_h = 220

    for i, coin in enumerate(data[:9]):
        cx = pad + (i % cols) * (card_w + pad)
        cy = 170 + (i // cols) * (card_h + pad)
        box = (cx, cy, cx+card_w, cy+card_h)

        neon_card(bg, box, (168,85,247))
        draw.rounded_rectangle(box, radius=26, fill=(11,16,32,235), outline=(56,189,248,200), width=2)

        try:
            logo = Image.open(io.BytesIO(requests.get(coin["image"], timeout=10).content)).convert("RGBA")
            logo = logo.resize((56,56))
            bg.alpha_composite(logo, (cx+22, cy+18))
        except:
            pass

        draw.text((cx+92, cy+20), f"{coin['name']} ({coin['symbol'].upper()})", fill=(220,230,255,255), font=name_font)
        price = f"${coin['current_price']:,}"
        draw.text((cx+22, cy+86), price, fill=(168,85,247,255), font=price_font)

        ch = coin.get("price_change_percentage_24h", 0) or 0
        emoji = "🟢" if ch >= 0 else "🔴"
        draw.text((cx+22, cy+146), f"24h {emoji} {ch:.2f}%", fill=(148,163,184,255), font=meta_font)

    buf = io.BytesIO()
    bg.convert("RGB").save(buf, format="PNG", quality=95)
    buf.seek(0)
    return buf

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_prices()
        img = generate_image(data)
        await update.message.reply_photo(photo=img, caption="⚡ Live Crypto Dashboard (16:9)")
    except Exception as e:
        await update.message.reply_text("⚠️ Dashboard render nahi ho pa raha. Thoda baad try karo.")
        print(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /prices — premium 16:9 crypto dashboard image milega 📸")

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
