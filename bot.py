import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BOT_TOKEN = "7663073456:AAGKttb2SAxgKozbEcit8a3xzBlkmu4Ua3U"

async def start(update: Update, context):
    await update.message.reply_text("Bada link bhejo, main short karke de dunga 😄")

async def shorten(update: Update, context):
    long_url = update.message.text.strip()
    api_url = f"https://tinyurl.com/api-create.php?url={long_url}"
    short_url = requests.get(api_url).text
    await update.message.reply_text(f"Short link: {short_url}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten))

app.run_polling()
