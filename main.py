from pyrogram import Client, filters
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PasswordHashInvalid,
    PhoneNumberInvalid
)
from pyromod import listen

API_ID = 21173110
API_HASH = "71db0c8aae15effc04dcfc636e68c349"
BOT_TOKEN = "2132657853:AAGE6D-W-1tbANoW2aZOf4wJPL-bT-1QnhQ"

app = Client(
    "session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)


@app.on_message(filters.command("start"))
async def start(client, message):

    phone_msg = await app.ask(
        message.chat.id,
        "📱 ارسل رقم الهاتف مع كود الدولة\nمثال:\n+201000000000"
    )

    phone = phone_msg.text

    user = Client(
        "user_session",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True
    )

    await user.connect()

    try:
        code = await user.send_code(phone)
    except PhoneNumberInvalid:
        return await message.reply("❌ الرقم غير صحيح")

    code_msg = await app.ask(
        message.chat.id,
        "💬 ارسل كود التحقق (يمكنك كتابته بأي شكل)"
    )

    login_code = "".join(filter(str.isdigit, code_msg.text))

    try:
        await user.sign_in(
            phone,
            code.phone_code_hash,
            login_code
        )

    except SessionPasswordNeeded:

        pass_msg = await app.ask(
            message.chat.id,
            "🔐 الحساب فيه تحقق بخطوتين\nارسل الباسورد"
        )

        try:
            await user.check_password(pass_msg.text)
        except PasswordHashInvalid:
            return await message.reply("❌ الباسورد خطأ")

    except (PhoneCodeInvalid, PhoneCodeExpired):
        return await message.reply("❌ الكود خطأ")

    session = await user.export_session_string()

    await user.send_message(
        "me",
        f"🔑 جلسة حسابك:\n\n`{session}`"
    )

    await user.disconnect()

    await message.reply("✅ تم توليد الجلسة وإرسالها للرسائل المحفوظة")


print("Bot Started")
app.run()
