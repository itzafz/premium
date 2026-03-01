import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ====== YAHAN APNI DETAILS BHARO ======
API_ID = 30536759            # yahan apna API_ID dalo (number)
API_HASH = "2633cf40ebefbc2a2b62a4439978e41c"  # yahan apna API_HASH dalo (string)
STRING_SESSION = "BQHR9DcAYKBUqtckjO1kAlwnx3GBLIXOSMSCl5BJaRZRHuGMEgE5FHadXLl2uIc67fYK95gD9thvdynjknRzXk4gv-7tmQXKQp7ZTEug0YX3ysTQjc49P6Ve3GMDFe5avRnzmGCX2I51p5LPcoIQoFjvkvkw3q9EUup7wsjvCnnW1i1tLHTGO5LoGeEWJLAmm8R2hShGpUw2TA1OPHsUDtD0FllxsieLtaZGnR09zlbBxEJu4DUjEoCUhYfQwdUJYmdIHAELzV1qqROTV5PMsS4R32KJBsFVPE3KqS4dBvsSPUE_HPq_EnS0san7mRBJPW09PJHlc1CSSXpPgZCcp3OKQNJ4bAAAAAHF5d9fAA"  # yahan apni StringSession paste karo
# ====================================

logging.basicConfig(level=logging.INFO)

if not isinstance(API_ID, int):
    raise ValueError("API_ID number hona chahiye")

if not API_HASH:
    raise ValueError("API_HASH missing")

if not STRING_SESSION:
    raise ValueError("STRING_SESSION missing")

print("STRING_SESSION length =", len(STRING_SESSION))

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if event.is_private:
        await event.reply("Join channel")

async def main():
    print("Starting userbot...")
    await client.start()
    print("Userbot running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
