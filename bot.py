import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7663073456:AAER0VSNRmDBpHnzWVXgqpZ"

async def ton_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd&include_24hr_change=true"
    r = requests.get(url).json()

    price = r["the-open-network"]["usd"]
    change = r["the-open-network"]["usd_24h_change"]

    msg = f"""
💎 TON Live Price

💰 Price: ${price}
📈 24h Change: {change:.2f}%

⏱ Updated: Just now
"""
    await update.message.reply_text(msg)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("ton", ton_price))

print("Bot is running...")
app.run_polling()
