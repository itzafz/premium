import os
import requests
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
    params = {
        "vs_currency": "usd",
        "ids": ids,
        "order": "market_cap_desc",
        "sparkline": "false"
    }
    r = requests.get(API_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Crypto Price Bot Ready!\n\n"
        "Commands:\n"
        "/prices - Live crypto prices\n"
        "/help - Help"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /prices to get live crypto prices.\n"
        "Auto data source: CoinGecko API"
    )

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_prices()
        msg = "📊 *Live Crypto Prices (USD)*\n\n"

        for coin in data:
            price = f"${coin['current_price']:,}"
            change = f"{coin.get('price_change_percentage_24h', 0):.2f}%"
            emoji = "🟢" if coin.get("price_change_percentage_24h", 0) >= 0 else "🔴"

            msg += (
                f"*{coin['name']}* ({coin['symbol'].upper()})\n"
                f"Price: `{price}`\n"
                f"24h: {emoji} {change}\n\n"
            )

        await update.message.reply_markdown(msg)

    except Exception as e:
        await update.message.reply_text("⚠️ Prices load nahi ho rahe. Baad me try karo.")
        print(e)

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN env variable missing")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("prices", prices))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
