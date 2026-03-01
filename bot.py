import os
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ========== CONFIG (Render Env Vars se aayega) ==========
api_id_raw = os.environ.get("API_ID", "").strip()
api_hash = os.environ.get("API_HASH", "").strip()
string_session = os.environ.get("STRING_SESSION", "").strip()
# ======================================================

logging.basicConfig(level=logging.INFO)

# ---- Strong validation ----
if not api_id_raw.isdigit():
    raise ValueError(f"Invalid API_ID: {repr(api_id_raw)}")

api_id = int(api_id_raw)

if not api_hash:
    raise ValueError("API_HASH missing. Render env vars check karo.")

if not string_session:
    raise ValueError("STRING_SESSION missing. Render env vars check karo.")

# Debug (temporary – deploy ke baad hata sakte ho)
print("STRING_SESSION length =", len(string_session))

try:
    session = StringSession(string_session)
except Exception as e:
    raise ValueError(f"Invalid STRING_SESSION format: {e}")

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
