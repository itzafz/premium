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

def load_font(size, weight="black"):
    # Always try EXTRA BOLD fonts first
    for path in (
        "assets/Inter-Black.ttf",
        "assets/DejaVuSans-Bold.ttf",
        "assets/Inter-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
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
    gdraw.rounded_rectangle(box, radius=28, fill=glow_color+(90,))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    base.alpha_composite(glow)

def draw_thick_text(draw, xy, text, font, fill, stroke_fill=(0,0,0), stroke_width=2):
    # Stroke = mota + readable
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)

def generate_image(data):
    W, H = 1920, 1080  # 16:9
    bg = gradient_bg(W, H).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    title_font = load_font(76)   # EXTRA BIG + THICK
    sub_font   = load_font(26)
    name_font  = load_font(30)
    price_font = load_font(52)   # THICK PRICE
    meta_font  = load_font(24)

    draw_thick_text(draw, (64, 36), "⚡ Crypto Dashboard", title_font, (220,235,255,255), stroke_width=3)
    draw_thick_text(draw, (64, 120), "Live market snapshot • Auto refresh", sub_font, (160,180,210,255), stroke_width=2)

    cols = 3
    pad = 36
    card_w = (W - pad*(cols+1)) // cols
    card_h = 240

    for i, coin in enumerate(data[:9]):
        cx = pad + (i % cols) * (card_w + pad)
        cy = 190 + (i // cols) * (card_h + pad)
        box = (cx, cy, cx+card_w, cy+card_h)

        neon_card(bg, box, (168,85,247))
        draw.rounded_rectangle(box, radius=28, fill=(11,16,32,235), outline=(56,189,248,220), width=3)

        try:
            logo = Image.open(io.BytesIO(requests.get(coin["image"], timeout=10).content)).convert("RGBA")
            logo = logo.resize((60,60))
            bg.alpha_composite(logo, (cx+24, cy+18))
        except:
            pass

        draw_thick_text(draw, (cx+96, cy+20), f"{coin['name']} ({coin['symbol'].upper()})", name_font, (230,240,255,255), stroke_width=2)
        price = f"${coin['current_price']:,}"
        draw_thick_text(draw, (cx+24, cy+92), price, price_font, (168,85,247,255), stroke_width=3)

        ch = coin.get("price_change_percentage_24h", 0) or 0
        emoji = "🟢" if ch >= 0 else "🔴"
        draw_thick_text(draw, (cx+24, cy+154), f"24h {emoji} {ch:.2f}%", meta_font, (170,185,210,255), stroke_width=2)

    buf = io.BytesIO()
    bg.convert("RGB").save(buf, format="PNG", quality=95)
    buf.seek(0)
    return buf

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_prices()
        img = generate_image(data)
        await update.message.reply_photo(photo=img, caption="⚡ Live Crypto Dashboard (16:9 • Bold Font)")
    except Exception as e:
        await update.message.reply_text("⚠️ Render fail ho gaya. Thoda baad try karo.")
        print(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /prices — mota/thick font wala premium dashboard milega 📸")

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
