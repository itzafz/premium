import os
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ========== CONFIG (Render Env Vars se aayega) ==========
api_id = int(os.environ.get("API_ID", "0"))
api_hash = os.environ.get("API_HASH", "")
string_session = os.environ.get("STRING_SESSION", "").strip()
# ======================================================

logging.basicConfig(level=logging.INFO)

if not api_id or not api_hash or not string_session:
    raise ValueError("API_ID / API_HASH / STRING_SESSION missing. Render env vars check karo.")

try:
    session = StringSession(string_session)
except Exception as e:
    raise ValueError(f"Invalid STRING_SESSION: {e}")

client = TelegramClient(session, api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    try:
        print("Message:", event.raw_text)
        await event.reply("I'm here")
    except Exception as e:
        print("Reply error:", e)

async def main():
    print("Starting userbot...")
    await client.start()
    print("Userbot is running. Send me a message!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
