from telethon import TelegramClient, events
from telethon.sessions import StringSession
import logging

# ========== CONFIG ==========
api_id = 30536759                 # <-- apna API ID daalo
api_hash = "2633cf40ebefbc2a2b62a4439978e41c"    # <-- naya API HASH daalo
string_session = "BQHR9DcASx0IkE0ulvfRfveQMU52vnFt3gG8v-4dYHLlz0xujmoUOwNYDN9gokW11fjgB6IKJQ8K682VHwrcCStQGkgvHWiEE5zke-9V_WsPioro66fq4vmUXzfc4-p-8a3CnXXoacXgF7gStxf24PQOPqSa_fREyDQLlxlpgBPPzV6Fi6-kaxC0xupem1Z9zYTaAXS6x5Kwj-q8oreGWSdEAJ00zzQ7Amebya0sJVUbmd-7lobfo_BS-kfq01UrdQo_zGXhXy4o9UogDu1vU_6SFFFjxH2JaHbMIYUotvNt1RjAaJihHd6dkbFcnHygdnrksnAJJbySOWhfHHF_XOvaIMYHGAAAAAHF5d9fAA"  # <-- Step 1 se mili string yahan paste karo
# ============================

logging.basicConfig(level=logging.INFO)

client = TelegramClient(StringSession(string_session), api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    try:
        print("Message:", event.raw_text)
        await event.reply("I'm here")
    except Exception as e:
        print("Reply error:", e)

print("Starting userbot...")
client.start()
print("Userbot is running. Send me a message!")
client.run_until_disconnected()
