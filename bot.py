from pyrogram import Client
import requests

api_id = 24526311
api_hash = "717d5df262e474f88d86c537a787c98d"
bot_token = "7663073456:AAER0VSNRmDBpHnzWVXgqpZ-y0zkE_sUf0g"

app = Client("fragment_checker_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message()
async def check_username(client, message):
    username = message.text.replace("@", "").strip()

    # Telegram username check
    try:
        await client.get_chat(username)
        await message.reply(f"❌ @{username} Telegram par taken hai")
    except:
        await message.reply(f"✅ @{username} Telegram par free lag raha hai")

app.run()
