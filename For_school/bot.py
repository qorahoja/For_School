import logging
import csv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# Bot toki (API token)ni quyidagi o'zgaruvchiga o'zgartiring
BOT_TOKEN = '6013857528:AAGH9iV9PI8WEg2-TCkNpxLOtWqSDQHgCmM'

# Bot obyekti yaratiladi
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

# Foydalanuvchi ma'lumotlarini saqlash uchun raqam holati
class Form:
    waiting_for_name = 1
    waiting_for_relation = 2
    waiting_for_share_contact = 3 # Yangi holat: aloqani tanlash

user_data = {}

# /start buyrug'iga javob berish
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykom! Men 129-maktab uchun yozilgan botman. Iltimos farzandingizni ismini kiriting: ")

    user_data[message.from_user.id] = {"state": Form.waiting_for_name}

# Foydalanuvchi xabarlari bilan ishlash
@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_name)
async def process_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    user_data[message.from_user.id]["state"] = Form.waiting_for_relation  # Aloqa holatini so'raganiz

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_father = types.KeyboardButton("Otasi🤵‍")
    button_mother = types.KeyboardButton("Onasi🧕")
    markup.row(button_father, button_mother)

    await message.reply(
        f"Siz {message.text}ga kim bolasiz?:",
        reply_markup=markup
    )

# Tugma javoblari uchun
@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_relation)
async def process_relation(message: types.Message):
    user_data[message.from_user.id]["relation"] = message.text
    user_data[message.from_user.id]["state"] = Form.waiting_for_share_contact  # Aloqani tanlagan keyin, raqamni so'raymiz

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    number = types.KeyboardButton("Raqamni jo'natish", request_contact=True)
    markup.row(number)

    await message.reply("Iltimos raqamingizni jo'nating", reply_markup=markup)

# Foydalanuvchi xabarlari bilan ishlash
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def process_phone(message: types.Message):
    user_id = message.from_user.id
    user_name = user_data[user_id]["name"]
    user_phone = message.contact.phone_number
    user_relation = user_data[user_id]["relation"]

    await message.answer(
        "Bergan ma'lumotlaringiz uchun rahmat farzandingiz <strong>davomati</strong> haqida ma'lumot u maktabga har kirganida va chiqganida sizga berib boriladi",
        parse_mode="html"
    )

    with open('users_data.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([user_name, user_phone, user_relation, user_id])

    user_data[user_id]["state"] = None
    user_data[user_id]["relation"] = None

if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
