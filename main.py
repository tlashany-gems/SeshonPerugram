from pyrogram import Client, filters

BOT_TOKEN = "8175656977:AAGYaBnd08Exerho1aYOOgGcFZVS1m5OG9w"

app = Client(
    "bot_session",
    bot_token=BOT_TOKEN,
    in_memory=True
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ البوت شغال! أرسل /session لتوليد الجلسة.")

@app.on_message(filters.command("session"))
async def session(client, message):
    await message.reply("⚡️ هنا سيتم توليد الجلسة لاحقًا")

print("Bot Started")
app.run()
