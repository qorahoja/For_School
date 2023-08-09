import logging
import csv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode

# Bot toki (API token)ni quyidagi o'zgaruvchiga o'zgartiring
BOT_TOKEN = '6013857528:AAGH9iV9PI8WEg2-TCkNpxLOtWqSDQHgCmM'

# Bot obyekti yaratiladi
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


# /start buyrug'iga javob berish
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Kontakt ma'lumotlarini jo'nating", request_contact=True)
    keyboard.add(button)

    await message.reply("Assalomu alaykom men 129-maktab uchun yozilgan botman iltimos bolangizni maktabga kelish ketishini bilmoqchi bo'lsangiz menga kontaktingizni yuboring:",
                        reply_markup=keyboard)
    await message.reply(
        "Sizga har kuni farzndingiz maktabga soat nechida va qachon kirayotgani va chiqayotganini aniq yetkazamiz:")



# Foydalanuvchi kontaktni jo'natganda ishlaydigan funksiya
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def process_contact(message: types.Message):
    contact = message.contact
    contact_info = f"Kontakt nomi: {contact.first_name}\nTelefon raqami: {contact.phone_number}"
    await message.reply( "Bizga ishonch bildirganingiz uchun rahmat")

    await message.reply(contact_info, parse_mode=ParseMode.MARKDOWN)

    # Kontakt ma'lumotlarini CSV faylga saqlash
    with open('users_data.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([contact.phone_number, contact.first_name])


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
