import os
import sqlite3
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import UsernameNotOccupied, UsernameInvalid
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("username_hunter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DB = "data.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        username TEXT,
        last_status TEXT,
        last_price TEXT
    )""")
    con.commit()
    con.close()

def add_wishlist(chat_id, username):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("INSERT INTO wishlist(chat_id, username, last_status, last_price) VALUES (?, ?, ?, ?)",
                (chat_id, username, "unknown", "unknown"))
    con.commit()
    con.close()

def get_wishlist(chat_id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT username FROM wishlist WHERE chat_id=?", (chat_id,))
    rows = cur.fetchall()
    con.close()
    return [r[0] for r in rows]

async def check_telegram(client, username):
    try:
        await client.get_chat(username)
        return "taken"
    except UsernameNotOccupied:
        return "free"
    except UsernameInvalid:
        return "invalid"
    except Exception:
        return "error"

# --- Fragment stub (Phase 2 me real scraper/API) ---
def check_fragment(username):
    # TODO: Playwright / HTML parse
    return {"status": "unknown", "price": None}

@app.on_message(filters.private & filters.text)
async def handler(client, message):
    text = message.text.strip()
    chat_id = message.chat.id

    if text.startswith("/start"):
        return await message.reply(
            "👋 Username Hunter Bot\n\n"
            "Commands:\n"
            "/add <username>\n"
            "/remove <username>\n"
            "/list\n"
            "/check <username>\n"
        )

    if text.startswith("/add"):
        u = text.split(maxsplit=1)[-1].replace("@", "")
        add_wishlist(chat_id, u)
        return await message.reply(f"⭐ @{u} wishlist me add ho gaya.")

    if text.startswith("/list"):
        items = get_wishlist(chat_id)
        if not items:
            return await message.reply("Wishlist empty hai.")
        return await message.reply("📌 Wishlist:\n" + "\n".join(f"- @{u}" for u in items))

    if text.startswith("/check"):
        u = text.split(maxsplit=1)[-1].replace("@", "")
        tg_status = await check_telegram(client, u)
        frag = check_fragment(u)
        return await message.reply(
            f"🔎 @{u}\n"
            f"Telegram: {tg_status}\n"
            f"Fragment: {frag['status']}\n"
            f"Price: {frag['price']}"
        )

# --- Daily checker job ---
async def daily_check():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT chat_id, username, last_status FROM wishlist")
    rows = cur.fetchall()
    con.close()

    for chat_id, username, last_status in rows:
        tg_status = await check_telegram(app, username)
        if tg_status == "free" and last_status != "free":
            await app.send_message(chat_id, f"🎉 @{username} ab Telegram par FREE ho gaya!")

        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("UPDATE wishlist SET last_status=? WHERE chat_id=? AND username=?",
                    (tg_status, chat_id, username))
        con.commit()
        con.close()

async def main():
    init_db()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_check, "interval", hours=24)
    scheduler.start()
    await app.start()
    print("Bot running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    app.run(main())
