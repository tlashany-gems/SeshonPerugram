from pyrogram import Client,filters
from pyrogram.errors import SessionPasswordNeeded,PhoneCodeExpired
from pyrogram.errors.exceptions.bad_request_400 import PasswordHashInvalid,PhoneCodeInvalid
from pyrogram.errors.exceptions.not_acceptable_406 import PhoneNumberInvalid
from pyromod import listen


API_ID = 21173110
API_HASH = "71db0c8aae15effc04dcfc636e68c349"
TOKEN = "8175656977:AAGYaBnd08Exerho1aYOOgGcFZVS1m5OG9w:"

app = Client("Session",api_id=API_ID,api_hash=API_HASH,bot_token=TOKEN, in_memory=True)


@app.on_message(filters.command("start"))
async def Send(app,msg):
  c = Client("Pyrogram",
  API_ID,API_HASH,
  device_model="Paddington3",
  in_memory=True)
  await c.connect()
  a = msg.text
  msg = await app.ask(msg.chat.id,f"يا {msg.from_user.mention} ارسل رقمك الان \n مثال : +20112801111",filters=filters.text)
  Number = msg.text
  
  try:
  	send = await c.send_code(Number)
  except PhoneNumberInvalid:
  	return await msg.reply("الرقم الذي ارسلته خاطئ",quote=True)
  except Exception:
         return await msg.reply("حدث خطا حاول مره اخري",quote=True)
  	
  SendCode = send.phone_code_hash
  code = await app.ask(msg.chat.id,f"يا {msg.from_user.mention} ارسل الان كود التحقق \n مثال : `1 2 3 4 5 6`",filters=filters.text)
  
  RecepionCode = code.text
  
  try:
  	await c.sign_in(Number,SendCode,RecepionCode)
  except SessionPasswordNeeded:
  	Password = await app.ask(msg.chat.id,f"يا {msg.from_user.mention} ارسل الان كود التحقق بخطوتين",filters=filters.text)
  	
  	PasswordAss = Password.text
  try:
  	await c.check_password(password=PasswordAss)
  except PasswordHashInvalid:
  	return await Password.reply("الباسورد خطأ",quote=True)
  except (PhoneCodeInvalid, PhoneCodeExpired):
    return await code.reply("الكود خطأ",quote=True)
         
  try:
  	await c.sign_in(Number,SendCode,RecepionCode)
  except:
  	pass
  
  a = await msg.reply("انتظر قليلا",quote=True)
  
  get = await c.get_me()
  text = "||**معلومات عنك**|| :\n\n"
  text += f"**اسمك الاول **: {get.first_name}\n"
  text += f"**ايديك **: {get.id}\n"
  text += f"**رقمك** : {Number}\n"
  text += f"\n\n شاهد الرسائل المحفوظه [{get.first_name}](tg://openmessage?user_id={get.id})\n"
  text += "للاستخراج مره اخر اضغط /start"
  
  Session = await c.export_session_string()
  await a.delete()
  
  await c.send_message("me",text=f"الجلسه الخاصه بك : \n\n||`{Session}`||\n\nلا تشارك هذا الكود مع احد \n معلومات عن المطور : @I0_I6")
  
  await c.disconnect()
  
  await app.send_message(msg.chat.id,text)
  
print("Run..")
app.run()
