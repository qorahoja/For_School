import logging
import csv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Bot toki (API token)ni quyidagi o'zgaruvchiga o'zgartiring
BOT_TOKEN = '6487765756:AAGwUvqglUMxsw0tVZ_DY29VRe_AQf-a4-s'

# Bot obyekti yaratiladi
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


# Foydalanuvchi ma'lumotlarini saqlash uchun raqam holati
class Form:
    waiting_for_name = 1
    waiting_for_relation = 2
    waiting_for_share_contact = 3
    waiting_for_teacher_name = 4
    waiting_for_teacher_phone = 5  # Yangi holat: aloqani tanlash


user_data = {}

# /start buyrug'iga javob berish
ROLES = ["Ustoz", "Ota-Ona"]


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    role_buttons = [types.KeyboardButton(role) for role in ROLES]
    markup.add(*role_buttons)

    markup_r = types.ReplyKeyboardRemove()

    user_id = message.from_user.id
    # Check if the user's chat ID is in the third column of users_data.csv
    with open('users_data.csv', 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if row[3] == str(user_id):
                await message.reply("Siz allaqachon ro'yhatdan o'tkansiz. Rahmat!", reply_markup=markup_r)
                break
        else:
            await message.reply("Assalomu alaykom! Kim sifatida ro'yhatdan o'tmoqchisiz?", reply_markup=markup)



@dp.message_handler(lambda message: message.text == "Ustoz")
async def process_ustoz_role(message: types.Message):
    markup = types.ReplyKeyboardRemove()
    selected_role = message.text
    user_data[message.from_user.id] = {"role": selected_role}
    user_data[message.from_user.id]["state"] = Form.waiting_for_teacher_name


    # Ustozlar ro'yhatida foydalanuvchi borligini tekshirish
    user_id = message.from_user.id

    found = False
    with open('teacherID.csv', 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if row[0] == str(user_id):
                await message.reply(f"Ustoz insmingizni kiriting", reply_markup=markup)
                found = True


                @dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_teacher_name)
                async def process_teacher_name(message: types.Message):
                    user_id = message.from_user.id
                    teacher_name = message.text

                    # teacher_name ma'lumotlarini saqlash yoki boshqa operatsiyalar

                    # Ma'lumotlarni user_data ga saqlash
                    if user_id in user_data:
                        user_data[user_id]["teacher_name"] = teacher_name  # Ma'lumotlarni user_data ga saqlash
                        user_data[user_id]["state"] = Form.waiting_for_teacher_phone

                        await message.answer("Ustozning telefon raqamini kiriting:")

                @dp.message_handler(
                    lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id][
                        "state"] == Form.waiting_for_teacher_phone)
                async def process_teacher_phone(message: types.Message):
                    user_id = message.from_user.id
                    teacher_phone = message.text

                    # teacher_phone ma'lumotlarini saqlash yoki boshqa operatsiyalar

                    # Ma'lumotlarni user_data ga saqlash
                    if user_id in user_data:
                        user_data[user_id]["teacher_phone"] = teacher_phone

                        # teachers_data.csv ga yozish
                        with open('teachers_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
                            csv_writer = csv.writer(csvfile)
                            csv_writer.writerow(
                                [user_data[user_id]["teacher_name"], user_data[user_id]["teacher_phone"], user_id])

                        user_data[user_id]["state"] = None

                        await message.answer("Ustozning ma'lumotlari saqlandi. Rahmat!")

                break

        if not found:
                await message.answer("siz ustozlar ro'yhatida yo'qsiz")






# Parent Role Selection Handler ("Ota-Ona")
@dp.message_handler(lambda message: message.text == "Ota-Ona")
async def process_ota_ona_role(message: types.Message):
    selected_role = message.text
    user_data[message.from_user.id] = {"role": selected_role, "state": Form.waiting_for_name}
    user_id = message.from_user.id

    found = False
    with open('parentsID.csv', 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if row[0] == str(user_id):
                markup = types.ReplyKeyboardRemove()  # Klaviaturani olib tashlash
                await message.reply("Iltimos, farzandingizni ismingizni kiriting:", reply_markup=markup)
                found = True

        if not found:
            await message.answer("Kechirasiz siz ota-onalar qatorida emassiz")








# Foydalanuvchi xabarlari bilan ishlash
@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_name)
async def process_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    user_data[message.from_user.id]["state"] = Form.waiting_for_relation

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_father = types.KeyboardButton("Otasi🤵‍")
    button_mother = types.KeyboardButton("Onasi🧕")
    markup.row(button_father, button_mother)

    await message.reply(
        f"Siz {message.text}ga kim bolasiz?:",
        reply_markup=markup
    )


# Tugma javoblari uchun
@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id][
    "state"] == Form.waiting_for_relation)
async def process_relation(message: types.Message):
    user_data[message.from_user.id]["relation"] = message.text
    user_data[message.from_user.id][
        "state"] = Form.waiting_for_share_contact  # Aloqani tanlagan keyin, raqamni so'raymiz

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
        "Bergan ma'lumotlaringiz uchun rahmat tez orada sizga farzandingiz haqida ma'lumot berishni boshlaymiz")

    with open('users_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([user_name, user_phone, user_relation, user_id])

    with open('parentsID.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([user_id])

    user_data[user_id]["state"] = None
    user_data[user_id]["relation"] = None





if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)