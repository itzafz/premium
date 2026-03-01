# bot.py
from pyrogram import Client, filters
import logging

API_ID = 30536759                 # number only
API_HASH = "2633cf40ebefbc2a2b62a4439978e41c"     # string
SESSION_STRING = "BQHR9DcAYKBUqtckjO1kAlwnx3GBLIXOSMSCl5BJaRZRHuGMEgE5FHadXLl2uIc67fYK95gD9thvdynjknRzXk4gv-7tmQXKQp7ZTEug0YX3ysTQjc49P6Ve3GMDFe5avRnzmGCX2I51p5LPcoIQoFjvkvkw3q9EUup7wsjvCnnW1i1tLHTGO5LoGeEWJLAmm8R2hShGpUw2TA1OPHsUDtD0FllxsieLtaZGnR09zlbBxEJu4DUjEoCUhYfQwdUJYmdIHAELzV1qqROTV5PMsS4R32KJBsFVPE3KqS4dBvsSPUE_HPq_EnS0san7mRBJPW09PJHlc1CSSXpPgZCcp3OKQNJ4bAAAAAHF5d9fAA"  # Pyrogram v2 session string

logging.basicConfig(level=logging.INFO)

app = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    in_memory=True
)

@app.on_message(filters.private & ~filters.me)
async def auto_reply(_, message):
    await message.reply_text("I’m okay, I’m online")

print("Userbot starting...")
app.run()
