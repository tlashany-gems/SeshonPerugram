from pyrogram import Client, filters
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PasswordHashInvalid,
    PhoneNumberInvalid
)
from pyromod import listen

# ضع هنا بيانات البوت التجريبي
BOT_TOKEN = "8581486539:AAF0YsMyVCrkrFvTNwV7neitXlXsZmyFNno"

# ملف البوت الرئيسي
app = Client(
    "session_bot",
    bot_token=BOT_TOKEN,
    in_memory=True
)

@app.on_message(filters.command("start"))
async def start(client, message):

    # طلب API_ID
    api_id_msg = await app.ask(message.chat.id, "ارسل الان API_ID")
    api_id = int(api_id_msg.text)

    # طلب API_HASH
    api_hash_msg = await app.ask(message.chat.id, "ارسل الان API_HASH")
    api_hash = api_hash_msg.text

    # طلب رقم الهاتف
    phone_msg = await app.ask(message.chat.id, "ارسل رقمك مثال:\n+201000000000")
    phone = phone_msg.text

    # إنشاء جلسة مستخدم
    user = Client(
        "user_session",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True
    )

    await user.connect()

    try:
        code_sent = await user.send_code(phone)
    except PhoneNumberInvalid:
        return await message.reply("❌ الرقم غير صحيح")

    # طلب الكود كل رقم على حدة
    code_msg = await app.ask(
        message.chat.id,
        "ارسل كود تسجيل الدخول بهذا الشكل:\n1 2 3 4 5"
    )

    login_code = code_msg.text.replace(" ", "")

    try:
        await user.sign_in(
            phone,
            code_sent.phone_code_hash,
            login_code
        )

    except SessionPasswordNeeded:
        # طلب باسورد التحقق بخطوتين
        pass_msg = await app.ask(
            message.chat.id,
            "🔐 ارسل باسورد التحقق بخطوتين"
        )

        try:
            await user.check_password(pass_msg.text)
        except PasswordHashInvalid:
            return await message.reply("❌ الباسورد خطأ")

    except (PhoneCodeInvalid, PhoneCodeExpired):
        return await message.reply("❌ الكود خطأ")

    # استخراج الجلسة
    session = await user.export_session_string()

    # ارسال الجلسة الى الرسائل المحفوظة
    await user.send_message(
        "me",
        f"🔑 جلسة حسابك:\n\n`{session}`"
    )

    await user.disconnect()

    await message.reply("✅ تم ارسال الجلسة الى الرسائل المحفوظة")

print("Bot Started")
app.run()
