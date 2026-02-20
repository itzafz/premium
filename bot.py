import os, io, requests, random, math
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
TON_API_URL = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"

# ---------- DATA ----------

def fetch_prices():
    ids = ",".join([c["id"] for c in COINS])
    r = requests.get(API_URL, params={"vs_currency": "usd", "ids": ids, "sparkline": "false"}, timeout=15)
    r.raise_for_status()
    return r.json()

def fetch_ton_fallback():
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

# ---------- UI ----------

def load_font(size):
    for path in ("assets/Inter-Bold.ttf", "assets/Inter-Regular.ttf", "assets/DejaVuSans.ttf"):
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()

def crypto_vibe_bg(w, h):
    base = Image.new("RGB", (w, h), "#060a14")
    draw = ImageDraw.Draw(base)

    # dark gradient
    for y in range(h):
        t = y / h
        col = (
            int(8*(1-t) + 24*t),
            int(12*(1-t) + 32*t),
            int(24*(1-t) + 56*t),
        )
        draw.line((0, y, w, y), fill=col)

    # aurora glow
    glow = Image.new("RGBA", (w, h), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for _ in range(5):
        cx, cy = random.randint(0, w), random.randint(0, h)
        r = random.randint(240, 380)
        col = random.choice([(56,189,248,90), (168,85,247,90), (34,197,94,80)])
        gd.ellipse((cx-r, cy-r, cx+r, cy+r), fill=col)
    glow = glow.filter(ImageFilter.GaussianBlur(80))

    # particles
    dots = Image.new("RGBA", (w, h), (0,0,0,0))
    dd = ImageDraw.Draw(dots)
    for _ in range(180):
        x,y = random.randint(0,w), random.randint(0,h)
        a = random.randint(80,160)
        dd.ellipse((x,y,x+2,y+2), fill=(255,255,255,a))

    bg = Image.alpha_composite(base.convert("RGBA"), glow)
    bg = Image.alpha_composite(bg, dots)
    return bg

def glass_neon_card(base, box):
    x1,y1,x2,y2 = box
    w,h = x2-x1, y2-y1

    # shadow
    shadow = Image.new("RGBA", base.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1+6,y1+10,x2+6,y2+10), radius=26, fill=(0,0,0,120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    base.alpha_composite(shadow)

    # glass fill
    layer = Image.new("RGBA", (w,h), (16,24,48,190))
    mask = Image.new("L", (w,h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,w,h), radius=26, fill=255)
    layer.putalpha(mask)
    base.alpha_composite(layer, (x1,y1))

    # soft neon edge
    glow = Image.new("RGBA", base.size, (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle(box, radius=26, fill=(99,102,241,70))
    glow = glow.filter(ImageFilter.GaussianBlur(16))
    base.alpha_composite(glow)

    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=26, outline=(120,150,255,140), width=2)

def draw_soft_text(draw, xy, text, font, fill):
    draw.text((xy[0]+1,xy[1]+1), text, font=font, fill=(0,0,0,160))
    draw.text(xy, text, font=font, fill=fill)

def human(n):
    if n >= 1e9: return f"{n/1e9:.2f}B"
    if n >= 1e6: return f"{n/1e6:.2f}M"
    if n >= 1e3: return f"{n/1e3:.2f}K"
    return str(int(n))

# ---------- DRAW ----------

def generate_image(data):
    W,H = 1920,1080
    bg = crypto_vibe_bg(W,H)
    draw = ImageDraw.Draw(bg)

    title_font = load_font(74)
    sub_font   = load_font(26)
    name_font  = load_font(30)
    price_font = load_font(52)
    meta_font  = load_font(22)

    draw_soft_text(draw, (64,36), "Crypto Pulse", title_font, (220,235,255,255))
    draw_soft_text(draw, (64,124), "Live market vibes • 24h change & volume", sub_font, (160,190,220,255))

    cols,pad,card_h = 3,36,250
    card_w = (W - pad*(cols+1)) // cols

    for i, coin in enumerate(data[:9]):
        cx = pad + (i % cols) * (card_w + pad)
        cy = 190 + (i // cols) * (card_h + pad)
        box = (cx, cy, cx+card_w, cy+card_h)

        glass_neon_card(bg, box)

        try:
            logo = Image.open(io.BytesIO(requests.get(coin["image"], timeout=10).content)).convert("RGBA").resize((56,56))
            bg.alpha_composite(logo, (cx+24, cy+18))
        except:
            pass

        draw_soft_text(draw, (cx+92, cy+22), f"{coin['name']} ({coin['symbol'].upper()})", name_font, (210,225,245,255))

        price_val = coin["current_price"]
        price_text = f"${price_val:.4f}" if coin["id"]=="toncoin" else f"${price_val:,}"
        draw_soft_text(draw, (cx+24, cy+92), price_text, price_font, (235,245,255,255))

        ch = coin.get("price_change_percentage_24h", 0) or 0
        arrow = "▲" if ch>=0 else "▼"
        ch_color = (120,220,170,255) if ch>=0 else (240,120,120,255)
        draw_soft_text(draw, (cx+24, cy+154), f"24h {arrow} {ch:.2f}%", meta_font, ch_color)

        vol = coin.get("total_volume", 0) or 0
        draw_soft_text(draw, (cx+24, cy+184), f"Vol: ${human(vol)}", meta_font, (170,195,220,255))

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
            ton = fetch_ton_fallback()
            data = [d for d in data if d["id"]!="toncoin"] + [ton]

        img = generate_image(data)
        await update.message.reply_photo(photo=img, caption="🔮 Crypto Pulse — premium crypto vibe dashboard (TON 4 decimals)")
    except Exception as e:
        await update.message.reply_text("⚠️ Dashboard render nahi ho pa raha. Thoda baad try karo.")
        print(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /prices — premium crypto vibe dashboard 🔮")

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
