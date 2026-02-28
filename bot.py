from telethon import TelegramClient, events

api_id = 30536759      # yahan apna API ID
api_hash = "2633cf40ebefbc2a2b62a4439978e41c"

client = TelegramClient("userbot", api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    await event.reply("I'm here")

client.start()
client.run_until_disconnected()
