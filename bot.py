import os, io, requests, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
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
TON_API_URL = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"

def fetch_prices():
    ids = ",".join([c["id"] for c in COINS if c["id"] != "toncoin"])
    r = requests.get(API_URL, params={"vs_currency": "usd", "ids": ids, "sparkline": "false"}, timeout=15)
    r.raise_for_status()
    data = r.json()

    ton = fetch_ton_from_tonapi()
    data.append(ton)
    return data

def fetch_ton_from_tonapi():
    r = requests.get(TON_API_URL, timeout=10)
    r.raise_for_status()
    price = float(r.json()["rates"]["ton"]["prices"]["usd"])
    return {
        "id": "toncoin",
        "name": "Toncoin",
        "symbol": "TON",
        "current_price": price,
        "price_change_percentage_24h": 0,
        "total_volume": 0,
        "image": "https://assets.coingecko.com/coins/images/17980/large/ton_symbol.png"
    }

# ---------- UI helpers (same as yours) ----------

def load_font(size):
    for path in ("assets/Inter-Black.ttf", "assets/DejaVuSans-Bold.ttf", "assets/Inter-Bold.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except:
            pass
    return ImageFont.load_default()

def cinematic_bg(w, h):
    base = Image.new("RGB", (w, h), "#060916")
    draw = ImageDraw.Draw(base)
    for y in range(h):
        r = int(6 + (28-6) * (y/h))
        g = int(9 + (36-9) * (y/h))
        b = int(22 + (68-22) * (y/h))
        draw.line((0, y, w, y), fill=(r, g, b))
    glow = Image.new("RGBA", (w, h), (0,0,0,0))
    gdraw = ImageDraw.Draw(glow)
    for _ in range(8):
        cx, cy = random.randint(0, w), random.randint(0, h)
        radius = random.randint(220, 380)
        color = random.choice([(56,189,248,80), (168,85,247,80), (34,197,94,70)])
        gdraw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    base = Image.alpha_composite(base.convert("RGBA"), glow)
    return base

def draw_thick_text(draw, xy, text, font, fill, stroke_width=2):
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=(0,0,0))

def human(n):
    if n >= 1e9: return f"{n/1e9:.2f}B"
    if n >= 1e6: return f"{n/1e6:.2f}M"
    if n >= 1e3: return f"{n/1e3:.2f}K"
    return str(int(n))

def generate_image(data):
    W, H = 1920, 1080
    bg = cinematic_bg(W, H)
    draw = ImageDraw.Draw(bg)
    title_font = load_font(78)
    name_font  = load_font(30)
    price_font = load_font(52)
    meta_font  = load_font(22)

    draw_thick_text(draw, (64, 36), "⚡ Crypto Dashboard (No API)", title_font, (230,240,255,255), 3)

    cols, pad, card_h = 3, 36, 250
    card_w = (W - pad*(cols+1)) // cols

    for i, coin in enumerate(data[:9]):
        cx = pad + (i % cols) * (card_w + pad)
        cy = 190 + (i // cols) * (card_h + pad)
        box = (cx, cy, cx+card_w, cy+card_h)

        draw.rounded_rectangle(box, radius=32, fill=(14,20,38,220), outline=(56,189,248,200), width=2)
        draw_thick_text(draw, (cx+24, cy+24), f"{coin['name']} ({coin['symbol']})", name_font, (235,245,255,255), 2)

        price_val = coin['current_price']
        price_text = f"${price_val:.4f}" if coin["id"]=="toncoin" else f"${price_val:,}"
        draw_thick_text(draw, (cx+24, cy+86), price_text, price_font, (168,85,247,255), 3)

        vol = coin.get("total_volume", 0) or 0
        draw_thick_text(draw, (cx+24, cy+148), f"Vol: ${human(vol)}", meta_font, (170,185,210,255), 2)

    buf = io.BytesIO()
    bg.convert("RGB").save(buf, format="PNG", quality=95)
    buf.seek(0)
    return buf

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_prices()
        img = generate_image(data)
        await update.message.reply_photo(photo=img, caption="⚡ Live Crypto Dashboard (No API Key)")
    except Exception as e:
        await update.message.reply_text("⚠️ Error aaya, baad me try karo.")
        print(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /prices — crypto dashboard without API key 🚀")

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN env variable missing")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prices", prices))
    print("🤖 Bot running (No API key)...")
    app.run_polling()

if __name__ == "__main__":
    main()
