import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import ContentTypeFilter
from aiogram.types import  ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from acsess import RAM


ram = RAM()

API_TOKEN = '6013857528:AAGH9iV9PI8WEg2-TCkNpxLOtWqSDQHgCmM'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")



@dp.message_handler(content_types = types.ContentType.CONTACT)
async def conatc_handler(message: types.Message):
    # raqmni saqlash
    phone_number = message.contact.phone_number

    remover = ReplyKeyboardRemove()
    await message.answer(f"Sini reamingz {phone_number}", reply_markup = remover)

@dp.message_handler()
async def core_message(message: types.Message):
    print(message.text)
    id = message.from_user.id
    if ram.check_user(id):
        if ram.get_action(user_id=id) == 'get_name':
            ism = message.text
            # ismni saqlash
            await message.answer(f"Ok end telefon raqamingzni yuboring", reply_markup = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = "Kontakni ulashish", request_contact = True)]], resize_keyboard = True))

        elif ram.get_action(user_id = id) == 'registr':
            ram.set_action(user_id = id, action = "get_name")
            await message.answer("Ilitmos Farzandingzni ismni kiriting!")
    else:
        ram.add_user(user_id = message.from_user.id, user_name = message.from_user.first_name)
        await  message.answer("Assalomu alykum, Iltimos farzand ism kirit")

    # await bot.send_message(chat_id = usr_id, text = "salom")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)