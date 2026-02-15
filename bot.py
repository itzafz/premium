import os
import sys
import signal
import asyncio
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.errors import UsernameNotOccupied, UsernameInvalid

# ---------- Graceful shutdown (Heroku) ----------
def shutdown_handler(sig, frame):
    print("Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

# ---------- Env vars ----------
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("Missing API_ID / API_HASH / BOT_TOKEN in env vars")

# ---------- Pyrogram client ----------
app = Client("username_hunter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------- Telegram availability (BOT-SAFE) ----------
async def check_telegram(client, username: str):
    try:
        await client.get_chat(username)
        return "taken"
    except UsernameNotOccupied:
        return "free"
    except UsernameInvalid:
        return "invalid"
    except Exception as e:
        print("TG check error (bot-safe):", e)
        # Ambiguous / multiple matches / private => taken (safe default)
        return "taken"

# ---------- Fragment checker (HTML scrape) ----------
def check_fragment(username: str):
    url = f"https://fragment.com/username/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; UsernameHunterBot/1.0)"
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            return {"status": "unknown", "price": None}

        soup = BeautifulSoup(r.text, "html.parser")
        page_text = soup.get_text(" ").lower()

        status = "not listed"
        price = None

        if "for sale" in page_text or "buy" in page_text:
            status = "for sale"
            for el in soup.find_all(["span", "div"]):
                t = el.get_text(strip=True)
                if t and "ton" in t.lower():
                    price = t
                    break
        elif "sold" in page_text:
            status = "sold"

        return {"status": status, "price": price}
    except Exception as e:
        print("Fragment error:", e)
        return {"status": "unknown", "price": None}

# ---------- Bot handlers ----------
@app.on_message(filters.private & filters.text)
async def handler(client, message):
    text = message.text.strip()

    if text.startswith("/start"):
        return await message.reply(
            "👋 **Username Hunter Bot**\n\n"
            "Use:\n"
            "• `/fragment <username>`\n\n"
            "Example:\n"
            "• `/fragment GolgiBody`\n\n"
            "Main bataunga:\n"
            "Telegram availability + Fragment status + price (TON).",
            disable_web_page_preview=True
        )

    if text.startswith("/fragment"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply("❌ Use: `/fragment <username>`")

        u = parts[1].replace("@", "").strip()

        # Basic validation
        if not (5 <= len(u) <= 32) or not u.replace("_", "").isalnum():
            return await message.reply("❌ Invalid username format.\nExample: my_name123")

        tg_status = await check_telegram(client, u)
        frag = check_fragment(u)

        return await message.reply(
            f"🔎 **@{u}**\n\n"
            f"Telegram: **{tg_status}**\n"
            f"Fragment: **{frag['status']}**\n"
            f"Price: **{frag['price'] or 'N/A'}**",
            disable_web_page_preview=True
        )

# ---------- App runner ----------
async def main():
    await app.start()
    print("Username Hunter Bot running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    app.run(main())
