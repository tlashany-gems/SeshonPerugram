from pyrogram import Client, filters

# ضع توكن البوت التجريبي
BOT_TOKEN = "8175656977:AAGYaBnd08Exerho1aYOOgGcFZVS1m5OG9w"

app = Client(
    "bot_session",
    bot_token=BOT_TOKEN,
    in_memory=True
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ البوت شغال! ارسل /session لعمل جلسة.")

@app.on_message(filters.command("session"))
async def session_generator(client, message):
    await message.reply("⚡️ وظيفة إنشاء الجلسة ستضاف لاحقًا في نسخة الإنتاج.")

print("Bot Started")
app.run()
