import os, io, requests, random, math
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
CMC_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
TON_API_URL = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"

# ---------- DATA ----------

def fetch_prices():
    ids = ",".join([c["id"] for c in COINS])
    r = requests.get(API_URL, params={"vs_currency": "usd", "ids": ids, "sparkline": "false"}, timeout=15)
    r.raise_for_status()
    return r.json()

def fetch_ton_from_cmc():
    api_key = os.environ.get("CMC_API_KEY")
    if not api_key:
        return None
    headers = {"X-CMC_PRO_API_KEY": api_key, "Accepts": "application/json"}
    r = requests.get(CMC_API_URL, headers=headers, params={"symbol": "TON", "convert": "USD"}, timeout=15)
    r.raise_for_status()
    q = r.json()["data"]["TON"]["quote"]["USD"]
    return {
        "id": "toncoin", "name": "Toncoin", "symbol": "TON",
        "current_price": float(q["price"]),
        "price_change_percentage_24h": q["percent_change_24h"],
        "total_volume": q["volume_24h"],
        "image": "https://assets.coingecko.com/coins/images/17980/large/ton_symbol.png"
    }

def fetch_ton_from_tonapi():
    r = requests.get(TON_API_URL, timeout=10)
    r.raise_for_status()
    price = float(r.json()["rates"]["ton"]["prices"]["usd"])
    return {
        "id": "toncoin", "name": "Toncoin", "symbol": "TON",
        "current_price": price,
        "price_change_percentage_24h": 0,
        "total_volume": 0,
        "image": "https://assets.coingecko.com/coins/images/17980/large/ton_symbol.png"
    }

# ---------- UI HELPERS ----------

def load_font(size):
    for path in ("assets/Inter-Black.ttf", "assets/DejaVuSans-Bold.ttf", "assets/Inter-Bold.ttf"):
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()

def cinematic_bg(w, h):
    base = Image.new("RGB", (w, h), "#060916")
    draw = ImageDraw.Draw(base)
    for y in range(h):
        t = y / h
        col = (
            int(8 + 30*t),
            int(10 + 35*t),
            int(28 + 70*t),
        )
        draw.line((0, y, w, y), fill=col)

    glow = Image.new("RGBA", (w, h), (0,0,0,0))
    gdraw = ImageDraw.Draw(glow)
    for _ in range(10):
        cx, cy = random.randint(0, w), random.randint(0, h)
        r = random.randint(220, 420)
        c = random.choice([(56,189,248,90), (168,85,247,90), (34,197,94,70)])
        gdraw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=c)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    return Image.alpha_composite(base.convert("RGBA"), glow)

def neon_gradient_card_layer(size, radius=28):
    w, h = size
    layer = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    for y in range(h):
        t = y / h
        r = int(120 + 60*math.sin(t*math.pi))
        g = int(100 + 120*t)
        b = int(180 + 60*(1-t))
        a = 210
        draw.line((0, y, w, y), fill=(r, g, b, a))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,w,h), radius=radius, fill=255)
    layer.putalpha(mask)
    return layer

def creative_neon_card(base, box):
    x1,y1,x2,y2 = box
    w,h = x2-x1, y2-y1

    glow = Image.new("RGBA", base.size, (0,0,0,0))
    g = ImageDraw.Draw(glow)
    g.rounded_rectangle(box, radius=30, fill=(99,102,241,120))
    g.rounded_rectangle((x1+6,y1+6,x2-6,y2-6), radius=26, fill=(56,189,248,80))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(glow)

    layer = neon_gradient_card_layer((w,h), radius=28)
    base.alpha_composite(layer, (x1,y1))

    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=28, outline=(56,189,248,220), width=2)

    shine = Image.new("RGBA", (w,h), (255,255,255,0))
    sdraw = ImageDraw.Draw(shine)
    sdraw.polygon([(0,0),(w,0),(w*0.6,h*0.35),(0,h*0.35)], fill=(255,255,255,26))
    base.alpha_composite(shine, (x1,y1))

# ---------- DRAW ----------

def draw_thick_text(draw, xy, text, font, fill, stroke_width=2):
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=(0,0,0))

def human(n):
    if n >= 1e9: return f"{n/1e9:.2f}B"
    if n >= 1e6: return f"{n/1e6:.2f}M"
    if n >= 1e3: return f"{n/1e3:.2f}K"
    return str(int(n))

def generate_image(data):
    W,H = 1920,1080
    bg = cinematic_bg(W,H)
    draw = ImageDraw.Draw(bg)

    title_font = load_font(78)
    sub_font   = load_font(26)
    name_font  = load_font(30)
    price_font = load_font(52)
    meta_font  = load_font(22)

    draw_thick_text(draw, (64,36), "⚡ Crypto Dashboard", title_font, (230,240,255,255), 3)
    draw_thick_text(draw, (64,124), "Live market snapshot • 24h Change & Volume", sub_font, (170,190,220,255), 2)

    cols,pad,card_h = 3,36,250
    card_w = (W - pad*(cols+1)) // cols

    for i, coin in enumerate(data[:9]):
        cx = pad + (i % cols) * (card_w + pad)
        cy = 190 + (i // cols) * (card_h + pad)
        box = (cx, cy, cx+card_w, cy+card_h)

        creative_neon_card(bg, box)

        try:
            logo = Image.open(io.BytesIO(requests.get(coin["image"], timeout=10).content)).convert("RGBA").resize((60,60))
            bg.alpha_composite(logo, (cx+24, cy+18))
        except:
            pass

        draw_thick_text(draw, (cx+96, cy+20), f"{coin['name']} ({coin['symbol'].upper()})", name_font, (235,245,255,255), 2)

        price_val = coin["current_price"]
        price_text = f"${price_val:.4f}" if coin["id"]=="toncoin" else f"${price_val:,}"
        draw_thick_text(draw, (cx+24, cy+92), price_text, price_font, (235,245,255,255), 3)

        ch = coin.get("price_change_percentage_24h", 0) or 0
        arrow = "▲" if ch>=0 else "▼"
        ch_color = (34,197,94,255) if ch>=0 else (239,68,68,255)
        draw_thick_text(draw, (cx+24, cy+154), f"24h {arrow} {ch:.2f}%", meta_font, ch_color, 2)

        vol = coin.get("total_volume", 0) or 0
        draw_thick_text(draw, (cx+24, cy+184), f"Vol: ${human(vol)}", meta_font, (200,210,230,255), 2)

    buf = io.BytesIO()
    bg.convert("RGB").save(buf, "PNG", quality=95)
    buf.seek(0)
    return buf

# ---------- BOT ----------

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_prices()
        ids = [d["id"] for d in data]
        ton_bad = any(d["id"]=="toncoin" and (not d.get("current_price") or d["current_price"]==0) for d in data)
        if "toncoin" not in ids or ton_bad:
            ton = None
            try: ton = fetch_ton_from_cmc()
            except: pass
            if not ton: ton = fetch_ton_from_tonapi()
            data = [d for d in data if d["id"]!="toncoin"] + [ton]

        img = generate_image(data)
        await update.message.reply_photo(photo=img, caption="⚡ Neon Crypto Dashboard (TON 4 decimals)")
    except Exception as e:
        await update.message.reply_text("⚠️ Dashboard render nahi ho pa raha. Thoda baad try karo.")
        print(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /prices — neon gradient crypto dashboard 🔥")

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
