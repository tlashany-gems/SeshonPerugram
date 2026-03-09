import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "2132657853:AAGE6D-W-1tbANoW2aZOf4wJPL-bT-1QnhQ"

bot = Client("session-bot", bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔑 Generate Pyrogram Session", callback_data="gen")]]
    )
    await message.reply_text(
        "اهلا بيك في بوت توليد الجلسات 🔐\nاضغط على الزر تحت للبدء",
        reply_markup=keyboard
    )

@bot.on_callback_query(filters.regex("gen"))
async def generate(client, callback):
    user_id = callback.from_user.id

    await callback.message.reply("📌 ابعت رقمك مع كود الدولة\nمثال: +201000000000")
    phone_msg = await client.ask(user_id)
    phone = phone_msg.text

    await callback.message.reply("📝 ابعت API_ID بتاعك")
    api_id_msg = await client.ask(user_id)
    api_id = int(api_id_msg.text)

    await callback.message.reply("🔑 ابعت API_HASH بتاعك")
    api_hash_msg = await client.ask(user_id)
    api_hash = api_hash_msg.text

    session = Client(":memory:", api_id=api_id, api_hash=api_hash)

    await session.connect()

    sent_code = await session.send_code(phone)

    await callback.message.reply("📩 ابعت كود التحقق اللي وصلك")
    code_msg = await client.ask(user_id)
    code = "".join(filter(str.isdigit, code_msg.text))

    try:
        await session.sign_in(
            phone,
            sent_code.phone_code_hash,
            code
        )
    except Exception as e:
        await callback.message.reply(f"❌ حصل خطأ:\n{e}")
        return

    string_session = await session.export_session_string()

    sent = await callback.message.reply_text(
        f"✅ تم إنشاء الجلسة بنجاح:\n\n`{string_session}`"
    )

    # حذف الرسالة بعد 60 ثانية
    await asyncio.sleep(60)
    await sent.delete()

    await session.disconnect()

bot.run()
