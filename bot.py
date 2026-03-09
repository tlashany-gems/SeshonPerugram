import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid,
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)

# ─── Config ───────────────────────────────────────────
BOT_TOKEN = "2132657853:AAGE6D-W-1tbANoW2aZOf4wJPL-bT-1QnhQ"
# ──────────────────────────────────────────────────────

WAIT_API_ID, WAIT_API_HASH, WAIT_PHONE, WAIT_CODE, WAIT_2FA = range(5)

user_data_store = {}

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 *Mira Music - String Session Generator*\n\n"
        "هولد لينك الجلسة لـ YukkiMusic/MiraMusic\n\n"
        "أول حاجة، ابعتلي الـ *API\\_ID* بتاعك\n"
        "_(هتلاقيه على my.telegram.org)_",
        parse_mode="Markdown"
    )
    return WAIT_API_ID

async def get_api_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ الـ API_ID لازم يكون أرقام بس! جرب تاني:")
        return WAIT_API_ID
    user_data_store[update.effective_user.id] = {"api_id": int(text)}
    await update.message.reply_text(
        "✅ تمام!\n\nدلوقتي ابعتلي الـ *API\\_HASH* بتاعك:",
        parse_mode="Markdown"
    )
    return WAIT_API_HASH

async def get_api_hash(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_data_store[update.effective_user.id]["api_hash"] = update.message.text.strip()
    await update.message.reply_text(
        "✅ تمام!\n\nدلوقتي ابعتلي *رقم التليفون* بتاع الحساب الثاني\n"
        "_(بالصيغة الدولية مثلاً: +201234567890)_",
        parse_mode="Markdown"
    )
    return WAIT_PHONE

async def get_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    phone = update.message.text.strip()
    data = user_data_store[uid]

    await update.message.reply_text("⏳ بيبعت الكود على تيليجرام...")

    try:
        client = Client(
            f"session_{uid}",
            api_id=data["api_id"],
            api_hash=data["api_hash"],
            in_memory=True
        )
        await client.connect()
        sent = await client.send_code(phone)
        data["phone"] = phone
        data["phone_code_hash"] = sent.phone_code_hash
        data["client"] = client
        await update.message.reply_text(
            "📱 تم إرسال الكود!\n\nابعتلي الكود اللي وصلك على تيليجرام:"
        )
        return WAIT_CODE
    except ApiIdInvalid:
        await update.message.reply_text("❌ الـ API_ID أو API_HASH غلط! ابدأ من أول بـ /start")
        return ConversationHandler.END
    except PhoneNumberInvalid:
        await update.message.reply_text("❌ رقم التليفون غلط! جرب تاني:")
        return WAIT_PHONE
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}\n\nابدأ من أول بـ /start")
        return ConversationHandler.END

async def get_code(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    code = update.message.text.strip().replace(" ", "")
    data = user_data_store[uid]
    client = data["client"]

    try:
        await client.sign_in(data["phone"], data["phone_code_hash"], code)
        session_string = await client.export_session_string()
        await client.disconnect()
        await update.message.reply_text(
            "✅ *تم توليد الـ String Session بنجاح!*\n\n"
            "انسخه وحطه في متغيرات Railway كـ `STRING_SESSION`\n\n"
            "⚠️ *لا تشاركه مع أي حد!*",
            parse_mode="Markdown"
        )
        await update.message.reply_text(f"`{session_string}`", parse_mode="Markdown")
        return ConversationHandler.END
    except PhoneCodeInvalid:
        await update.message.reply_text("❌ الكود غلط! جرب تاني:")
        return WAIT_CODE
    except PhoneCodeExpired:
        await update.message.reply_text("❌ الكود انتهى! ابدأ من أول بـ /start")
        return ConversationHandler.END
    except SessionPasswordNeeded:
        await update.message.reply_text(
            "🔐 حسابك عنده Two-Step Verification\n\nابعتلي الباسورد:"
        )
        return WAIT_2FA
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}\n\nابدأ من أول بـ /start")
        return ConversationHandler.END

async def get_2fa(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    password = update.message.text.strip()
    data = user_data_store[uid]
    client = data["client"]

    try:
        await client.check_password(password)
        session_string = await client.export_session_string()
        await client.disconnect()
        await update.message.reply_text(
            "✅ *تم توليد الـ String Session بنجاح!*\n\n"
            "انسخه وحطه في متغيرات Railway كـ `STRING_SESSION`\n\n"
            "⚠️ *لا تشاركه مع أي حد!*",
            parse_mode="Markdown"
        )
        await update.message.reply_text(f"`{session_string}`", parse_mode="Markdown")
        return ConversationHandler.END
    except PasswordHashInvalid:
        await update.message.reply_text("❌ الباسورد غلط! جرب تاني:")
        return WAIT_2FA
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}\n\nابدأ من أول بـ /start")
        return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم الإلغاء. ابدأ من أول بـ /start")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAIT_API_ID:   [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_id)],
            WAIT_API_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_hash)],
            WAIT_PHONE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            WAIT_CODE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code)],
            WAIT_2FA:      [MessageHandler(filters.TEXT & ~filters.COMMAND, get_2fa)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    print("✅ البوت شغال!")
    app.run_polling()

if __name__ == "__main__":
    main()
