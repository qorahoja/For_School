import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
import sqlite3
import secrets
import matplotlib.pyplot as plt
import os
# Bot token (API token)
BOT_TOKEN = '6438847465:AAHdcXrn7sKkDvYgCqsINkRfVOqdgUfWzSA'

# Bot object creation
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

# User data storage
class Form:
    waiting_for_name = 1
    waiting_for_relation = 2
    waiting_for_share_contact = 3
    waiting_for_teacher_name = 4
    waiting_for_teacher_phone = 5
    waiting_for_class = 6
    waiting_for_class_name = 7
    waiting_for_teacher_class = 8
    waiting_for_teacher_class_name = 9
    waiting_for_family_name = 10
    waiting_for_scholl_number = 11
    waiting_for_phone = 12
    waiting_for_pass = 13
    waiting_for_teacher_pass = 14
    waiting_for_analsys = 15
    waiting_for_dr = 16
    waiting_for_class_name_dir = 17
    waiting_for_class_dir = 18
    waiting_for_classDir = 19
    waiting_for_scholl_number_teacher = 20
    waiting_for_contct = 21
    teacher_verified = 22


user_data = {}

# Initialize SQLite database
conn = sqlite3.connect('school_data.db')
cursor = conn.cursor()

# Create tables if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        user_id INTEGER PRIMARY KEY,
        teacher_name TEXT,
        teacher_phone TEXT,
        teacher_class TEXT,
        teacher_class_name TEXT,
        school_number TEXT,
        pass TEXT
    )
''')

# Update the part of the database setup code

# Create tables if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS directors (
        user_id INTEGER PRIMARY KEY,
        director_name TEXT,
        director_phone TEXT,
        school_number TEXT,
        pass TEXT
    )
''')



cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_name TEXT,
        user_phone TEXT,
        user_relation TEXT,
        user_class TEXT,
        user_classname TEXT,
        user_family_name TEXT,
        scholl_number TEXT
    )
''')

conn.commit()

# /start command response
ROLES = ["Ustoz", "Ota-Ona", "Director"]
class_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
class_name_list = ["A", "B", "V"]
scholl_numbers = ['1', '2', '3', '4']







@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    role_buttons = [types.KeyboardButton(role) for role in ROLES]
    back = '🔙 Boshiga'

    markup.add(*role_buttons, back)

    markup_r = types.ReplyKeyboardRemove()

    user_id = message.from_user.id
    # Initialize SQLite database connection
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()

    try:
        # Check if the user's chat ID is in the directors table
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            await message.reply("Siz allaqachon ro'yhatdan o'tkansiz. Rahmat!", reply_markup=markup_r)
        else:
            
            await message.reply("Assalomu alaykom! Kim sifatida ro'yhatdan o'tmoqchisiz?", reply_markup=markup)
    finally:
        # Close the SQLite connection in the finally block to ensure it is always closed
        conn.close()










@dp.message_handler(lambda message: message.text == "Director")
async def process_director_role(message: types.Message):
    selected_role = message.text
    user_data[message.from_user.id] = {"role": selected_role, "state": Form.waiting_for_dr}
    user_id = message.from_user.id
    # Initialize SQLite database connection
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    try:
        # Check if the user's chat ID is in the directors table
        cursor.execute('SELECT user_id, pass FROM directors WHERE user_id = ?', (user_id,))
        director_data = cursor.fetchone()
        if director_data:
            user_data[user_id]["director_password"] = director_data[1]  # Store the director's password
            markup_re = types.ReplyKeyboardRemove()
            await message.reply("Iltimos, direktor parolingizni kiriting:", reply_markup=markup_re)
        else:

            await message.reply("Sizda direktorlik huquqi yo'q. Ma'lumotlarni o'zgartirishga sizda ruxsat yo'q.")
            return
    finally:
        # Close the SQLite connection in the finally block to ensure it is always closed
        conn.close()




@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_dr)
async def process_director_school_number(message: types.Message):
    user_id = message.from_user.id
    entered_password = message.text

    # Initialize SQLite database connection
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()

    try:
        # Check if the entered password is correct for the director
        global director_data
        cursor.execute('SELECT director_name, director_phone, school_number FROM directors WHERE user_id = ? AND pass = ?', (user_id, entered_password))
        director_data = cursor.fetchone()
    

        if director_data:
            director_info = f"Director: {director_data[0]}\nPhone: {director_data[1]}\nSchool Number: {director_data[2]}"
            await message.reply(director_info)

            # Add buttons for daily and weekly statistics
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            daily_button = types.KeyboardButton("Bugungi hisobot")
            back = '🔙 Boshiga'
 

            markup.row(daily_button, back)

            await message.reply("Statistika uchun tugmalarni tanlang:", reply_markup=markup)
        else:
            # Password is incorrect
            await message.reply("Parol noto'g'ri. Iltimos, qaytadan kiriting.")
    finally:
        # Close the SQLite connection in the finally block to ensure it is always closed
        conn.close()

    # Reset the director's password from user_data
    del user_data[user_id]["director_password"]
    user_data[user_id]["state"] = None




# ...

@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] is None)
async def process_general_commands(message: types.Message):
    if message.text == "Bugungi hisobot":
        user_id = message.from_user.id
        user_data[user_id]["state"] = Form.waiting_for_classDir


        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        role_buttons = [types.KeyboardButton(role) for role in class_list]
        back = '🔙 Boshiga'
        markup.add(*role_buttons, back)
        # Prompt the user to enter the class number
        await message.reply("Iltimos, sinfni tanlang", reply_markup=markup)

@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_classDir)
async def process_class_number(message: types.Message):
    user_id = message.from_user.id
    class_number = message.text

    # Check if the entered class number is valid
    if class_number not in class_list:
        await message.reply("Noto'g'ri sinf raqami. Iltimos, qaytadan kiriting (1-11):")
        return

    user_data[user_id]["selected_class"] = class_number
    user_data[user_id]["state"] = Form.waiting_for_class_name_dir

    # Provide buttons for selecting the class name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    class_name_buttons = [types.KeyboardButton(class_name) for class_name in class_name_list]

    back = '🔙 Boshiga'
    markup.row(*class_name_buttons, back)

    await message.reply("Iltimos, sinf nomini tanlang:", reply_markup=markup)

@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_class_name_dir)
async def process_class_name(message: types.Message):
    user_id = message.from_user.id
    class_name = message.text

    # Check if the entered class name is valid
    if class_name not in class_name_list:
        await message.reply("Noto'g'ri sinf nomi. Iltimos, qaytadan kiriting (A, B, V):")
        return

    user_data[user_id]["selected_class_name"] = class_name
    user_data[user_id]["state"] = None

    # Analyze attendance data and create visualizations
    analysis_results = analyze_attendance(user_data[user_id]["selected_class"], user_data[user_id]["selected_class_name"], f"{director_data[2]}.db")

    # Send the analysis results and visualizations to the director
    await send_analysis_results(user_id, analysis_results)
 

    # Reset the selected class and class name from user_data
    del user_data[user_id]["selected_class"]
    del user_data[user_id]["selected_class_name"]

# Function to analyze attendance data
def analyze_attendance(selected_class, selected_class_name, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Assuming detection_faces table contains the names of students who attended
    cursor.execute('SELECT name FROM detected_faces')
    present_students = [row[0] for row in cursor.fetchall()]

    # Get all students in the selected class and class name from the users table
    cursor.execute('''
        SELECT user_name FROM users
        WHERE user_class = ? AND user_classname = ?
    ''', (selected_class, selected_class_name))
    all_students = [row[0] for row in cursor.fetchall()]

    # Identify students who did not attend
    absent_students = list(set(all_students) - set(present_students))

    # Create a simple analysis result
    analysis_results = {
        "total_students": len(all_students),
        "present_students": len(present_students),
        "absent_students": len(absent_students),
        "absent_students_list": absent_students
    }

    # Close the SQLite connection
    conn.close()

    return analysis_results

# Function to send analysis results and visualizations to the director
# ... (previous code)

# Function to send analysis results and visualizations to the director
async def send_analysis_results(user_id, analysis_results):
    # Extract analysis results
    total_students = analysis_results["total_students"]
    present_students = analysis_results["present_students"]
    absent_students = analysis_results["absent_students"]
    absent_students_list = analysis_results["absent_students_list"]

    # Create a pie chart using Matplotlib
    labels = ["Kelganlar", "Kelmaganlar"]
    sizes = [present_students, absent_students]
    explode = (0.1, 0)  # explode the 1st slice (Present)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the chart to a file
    chart_file_path = "attendance_chart.png"
    plt.savefig(chart_file_path)
    plt.close()

    # Send the analysis results and chart to the director
    analysis_message = (
        f"Analysis:\n"
        f"Barcha o'quvchilar soni: {total_students}\n"
        f"Bugun kelgan o'quvchilar: {present_students}\n"
        f"Bugun kelmagan o'quvchilar: {absent_students}\n"
        f"Kelmagan o'quvchilarning ismlari: {', '.join(absent_students_list)}"
    )




    await bot.send_message(user_id, analysis_message)

    # Send the chart image to the director
    with open(chart_file_path, "rb") as chart_file:
                await bot.send_photo(user_id, chart_file)

    # Remove the temporary chart file
    os.remove(chart_file_path)



@dp.message_handler(commands=['reg_ustoz'])
async def reg_teacher(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]["state"] = Form.waiting_for_teacher_name

    # Initialize SQLite database connection
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()

    try:
        # Check if the user's chat ID is in the teachers table
        cursor.execute('SELECT user_id FROM teachers WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            await message.reply("Siz allaqachon ro'yhatdan o'tkansiz. Rahmat!")
        else:
            back = "🔙 Boshiga"

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            role_buttons = [types.KeyboardButton(role) for role in class_list]
            markup.add(*role_buttons, back)
            await message.reply("Iltimos, o'zingizni o'qitishga qarashli sinfni tanlang:", reply_markup=markup)

    finally:
        # Close the SQLite connection in the finally block to ensure it is always closed
        conn.close()

# Handle teacher class selection
@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_teacher_name)
async def process_teacher_class(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["state"] = Form.waiting_for_teacher_class

    # Store the selected teacher class
    user_data[user_id]["selected_teacher_class"] = message.text

    # Provide buttons for selecting the class name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    class_name_buttons = [types.KeyboardButton(class_name) for class_name in class_name_list]
    back = '🔙 Boshiga'
    markup.row(*class_name_buttons, back)

    await message.reply("Iltimos, sinf nomini tanlang:", reply_markup=markup)



@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_teacher_class)
async def scholl_number_techer(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["state"] = Form.waiting_for_scholl_number_teacher

    user_data[user_id]["selected_teacher_class_name"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    school_number_buttons = [types.KeyboardButton(num) for num in scholl_numbers]
    back = '🔙 Boshiga'
    markup.add(*school_number_buttons, back)

    await message.answer("Iltimos qayssi maktabda dars berishingizni tanlang: ", reply_markup=markup)

    



# Handle teacher class name selection
@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_scholl_number_teacher)
async def process_teacher_class_name(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["state"] = None
    user_data[user_id]["state"] = Form.waiting_for_contct

    # Store the selected teacher class name


    user_data[user_id]["selected_school_number"] = message.text


    # Request contact information
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    number = types.KeyboardButton("Raqamni jo'natish", request_contact=True)
    back = '🔙 Boshiga'
    markup.row(number, back)

    await message.reply("Iltimos, raqamingizni jo'nating", reply_markup=markup)

# Handle teacher contact information
@dp.message_handler(content_types=types.ContentType.CONTACT, state="waiting_for_contct")
async def process_teacher_contact(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    teacher_name = message.from_user.full_name
    teacher_phone = message.contact.phone_number
    teacher_class = user_data[user_id]["selected_teacher_class"]
    teacher_class_name = user_data[user_id]["selected_teacher_class_name"]
    scholl_number_techer = user_data[user_id]['selected_school_number']

    # Generate a random password
    random_password = secrets.token_hex(4)

    await message.answer(
        f"Muvaffaqiyatli ro'yhatdan o'tdingiz. Rahmat!\n"
        f"Bu sizning parolingiz: <br>{random_password}<br> iltimos uni saqlab oling"
    )

    # Initialize SQLite database connection
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()

    try:
        # Insert teacher information into the database
        cursor.execute('''
            INSERT INTO teachers (user_id, teacher_name, teacher_phone, teacher_class, teacher_class_name, school_number, pass)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, teacher_name, teacher_phone, teacher_class, teacher_class_name, scholl_number_techer,  random_password))

        conn.commit()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        # Handle the error (log it, send a message to the user, etc.)

    finally:
        # Close the SQLite connection in the finally block to ensure it is always closed
        conn.close()

    # Reset user state and data
    await state.finish()
    del user_data[user_id]["selected_teacher_class"]
    del user_data[user_id]["selected_teacher_class_name"]



@dp.message_handler(lambda message: message.text == '🔙 Boshiga', state='*')
async def back_to_main_menu(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    prev_state = await state.get_data()
    if prev_state:
        await state.set_state(prev_state['state'])
        await state.set_data(prev_state['prev_state_data'])
    else:
        await state.finish()
    await main_menu(message, state, text='Main menu')


# Your main_menu function
async def main_menu(message: types.Message, state: FSMContext, text='Main menu'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    role_buttons = [types.KeyboardButton(role) for role in ROLES]
    back = "🔙 Boshiga"
    markup.add(*role_buttons, back)

    markup_r = types.ReplyKeyboardRemove()

    user_id = message.from_user.id
    # Initialize SQLite database connection
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()

    try:
        # Check if the user's chat ID is in the directors table
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            await message.reply("Siz allaqachon ro'yhatdan o'tkansiz. Rahmat!", reply_markup=markup_r)
        else:
            
            await message.reply("Boshidasiz", reply_markup=markup)
    finally:
        # Close the SQLite connection in the finally block to ensure it is always closed
        conn.close()


    







@dp.message_handler(lambda message: message.text == "Ustoz")
async def log_teacher(message: types.Message):
    user_id = message.from_user.id

    if user_data.get(user_id) and user_data[user_id].get("state") == Form.teacher_verified:
        # Teacher is already verified
        await message.reply("Siz allaqachon tizimga kirdingiz. Further actions can be implemented here.")
        return

    user_data[user_id] = {"state": Form.waiting_for_teacher_pass}
    
    # Initialize SQLite database connection
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()

    try:
        # Check if the user's chat ID is in the teachers table
        cursor.execute('SELECT user_id, pass FROM teachers WHERE user_id = ?', (user_id,))
        teacher_data = cursor.fetchone()

        if teacher_data:
            user_data[user_id]["teacher_password"] = teacher_data[1]  # Store the teacher's password
            markup = types.ReplyKeyboardRemove()
            await message.reply("Iltimos, Ustoz parolingizni kiriting:", reply_markup=markup)
        else:
            await message.reply("Sizda Ustozlik huquqi yo'q. Ma'lumotlarni o'zgartirishga sizda ruxsat yo'q.")
            return
    finally:
        conn.close()

@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_teacher_pass)
async def process_teacher_password(message: types.Message):
    user_id = message.from_user.id
    entered_password = message.text

    # Check if the password has already been verified


    # Check if the entered password is correct for the teacher
    if entered_password == user_data[user_id]["teacher_password"]:
        user_data[user_id]["teacher_verified"] = True  # Mark the password as verified
        user_data[user_id]["state"] = Form.teacher_verified  # Update the user's state
        conn = sqlite3.connect('school_data.db')
        cursor = conn.cursor()

        try:
            # Fetch data for the specific teacher using user_id
            cursor.execute('SELECT teacher_name, teacher_phone, teacher_class, teacher_class_name, school_number FROM teachers WHERE user_id = ?', (user_id,))
            data = cursor.fetchone()

            if data:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                report = types.KeyboardButton("Sinfim hisoboti")
                back = "🔙 Boshiga"
                markup.add(report, back)

                teacher_info = f"Ism: {data[0]}\nTelefon raqami: {data[1]}\nSinf rahbarligi: {data[2]} {data[3]}"
                await bot.send_message(user_id, teacher_info, reply_markup=markup)
            else:
                await message.reply("Teacher data not found.")
        finally:
            conn.close()
    else:
        # Password is incorrect
        await message.reply("Parol noto'g'ri. Iltimos, qaytadan kiriting.")


@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.teacher_verified)
async def process_teacher_commands(message: types.Message):
    user_id = message.from_user.id

    if message.text == "Sinfim hisoboti":
        conn = sqlite3.connect('school_data.db')
        cursor = conn.cursor()

        try:
            global data
            
            # Fetch data for the specific teacher using user_id
            cursor.execute('SELECT teacher_name, teacher_phone, teacher_class, teacher_class_name, school_number FROM teachers WHERE user_id = ?', (user_id,))
            data = cursor.fetchone()

            if data:
                # Assuming analyze_attendance_teacher and send_result functions are defined elsewhere
                analiz = analyze_attendance_teacher(data[2], data[3])
                await send_result(user_id, analiz)
            else:
                await bot.send_message(user_id, "Teacher data not found.")
        finally:
            conn.close()




def analyze_attendance_teacher(teacher_class, teacher_classname):
    db_file = f"{data[4]}.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Step 1: Retrieve Data from detected_faces Table
    cursor.execute("SELECT name FROM detected_faces WHERE user_class = ? AND user_classname = ?", (teacher_class, teacher_classname))
    detected_faces_names = [row[0] for row in cursor.fetchall()]

    # Step 2: Retrieve Data from users Table
    cursor.execute("SELECT user_name FROM users WHERE user_class = ? AND user_classname = ?", (teacher_class, teacher_classname))
    users_names = [row[0] for row in cursor.fetchall()]

    # Step 3: Compare user_name in detected_faces with users
    arrivals = [user_name for user_name in users_names if user_name in detected_faces_names]
    absentees = [user_name for user_name in users_names if user_name not in detected_faces_names]

    # Close the connection
    conn.close()

    # Return the results as a dictionary
    return {
        "total_students": len(users_names),
        "present_students": len(arrivals),
        "absent_students": len(absentees),
        "absent_students_list": absentees
    }



async def send_result(user_id, analysis_results):
    # Extract analysis results
    total_students = analysis_results["total_students"]
    present_students = analysis_results["present_students"]
    absent_students = analysis_results["absent_students"]
    absent_students_list = analysis_results["absent_students_list"]

    # Create a pie chart using Matplotlib
    labels = ["Kelganlar", "Kelmaganlar"]
    sizes = [present_students, absent_students]
    explode = (0.1, 0)  # explode the 1st slice (Present)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the chart to a file
    chart_file_path = "attendance_chart.png"
    plt.savefig(chart_file_path)
    plt.close()

    # Send the analysis results and chart to the director
    analysis_message = (
        f"Analysis:\n"
        f"Barcha o'quvchilar soni: {total_students}\n"
        f"Bugun kelgan o'quvchilar: {present_students}\n"
        f"Bugun kelmagan o'quvchilar: {absent_students}\n"
        f"Kelmagan o'quvchilarning ismlari: {', '.join(absent_students_list)}"
    )

    await bot.send_message(user_id, analysis_message)

    # Send the chart image to the director
    with open(chart_file_path, "rb") as chart_file:
        await bot.send_photo(user_id, chart_file)

    # Remove the temporary chart file
    os.remove(chart_file_path)


# Ota-Ona ro'yhatida foydalanuvchi borligini tekshirish
@dp.message_handler(lambda message: message.text == "Ota-Ona")
async def process_ota_ona_role(message: types.Message):
    selected_role = message.text
    user_data[message.from_user.id] = {"role": selected_role, "state": Form.waiting_for_name}

    markup = types.ReplyKeyboardRemove()
    await message.reply("Iltimos, farzandingizni ismingizni kiriting:", reply_markup=markup)



# Foydalanuvchi xabarlari bilan ishlash
@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id][
    "state"] == Form.waiting_for_name)
async def process_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    user_data[message.from_user.id]["state"] = Form.waiting_for_family_name
    global ism
    ism = message.text

    markup = types.ReplyKeyboardRemove()
    await message.reply(
        f"Iltimos, {message.text}ning familyasini kiriting:",
        reply_markup=markup
    )

@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id][
    "state"] == Form.waiting_for_family_name)
async def process_family_name(message: types.Message):
    user_data[message.from_user.id]["family_name"] = message.text
    user_data[message.from_user.id]["state"] = Form.waiting_for_relation
    familya = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_father = types.KeyboardButton("Otasi🤵‍")
    button_mother = types.KeyboardButton("Onasi🧕")
    back = '🔙 Boshiga'
    markup.row(button_father, button_mother, back)

    await message.reply(
        f"Siz {ism} {familya}ga kim bolasiz?:",
        reply_markup=markup
    )


@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id]["state"] == Form.waiting_for_relation)
async def process_scholl_numbe(message: types.Message):
    user_data[message.from_user.id]['relation'] = message.text
    user_data[message.from_user.id]['state'] = Form.waiting_for_scholl_number

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = "🔙 Boshiga"


    scholl_number_buttons = [types.KeyboardButton(num) for num in scholl_numbers]
    markup.add(*scholl_number_buttons, back)

    await message.reply("Iltimos farzandingiz o'qidigan maktab raqamini tanlang:", reply_markup=markup)

@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id][
    "state"] == Form.waiting_for_scholl_number)
async def process_relation(message: types.Message):
    user_data[message.from_user.id]["scholl_number"] = message.text
    user_data[message.from_user.id]["state"] = Form.waiting_for_class

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    role_buttons = [types.KeyboardButton(role) for role in class_list]
    back = "🔙 Boshiga"
    markup.add(*role_buttons, back)

    await message.reply(
        f"Iltimos farzandingiz o'qdigan sinfni tanlang",
        reply_markup=markup
    )

@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id][
    "state"] == Form.waiting_for_class)
async def process_class(message: types.Message):
    user_data[message.from_user.id]["class"] = message.text
    user_data[message.from_user.id]["state"] = Form.waiting_for_class_name

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = "🔙 Boshiga"
    role_buttons = [types.KeyboardButton(role) for role in class_name_list]
    markup.add(*role_buttons, back)

    await message.reply(
        f"Farzandingiz {message.text} nimada oqidi",
        reply_markup=markup
    )

# ...

@dp.message_handler(lambda message: user_data.get(message.from_user.id) and user_data[message.from_user.id][
    "state"] == Form.waiting_for_class_name)
async def process_class_name(message: types.Message):
    user_id = message.from_user.id
    user_name = user_data[user_id]["name"]
    user_class = user_data[user_id]["class"]
    user_family_name = user_data[user_id]["family_name"]

    user_data[user_id]["class_name"] = message.text
    user_data[user_id]["state"] = Form.waiting_for_share_contact

    class_name = user_data[user_id]["class_name"]

    # Initialize SQLite database connection
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()

    try:
        # Foydalanuvchi sinfi va sinf nomini tekshiramiz
        if class_name in class_name_list and user_class in class_list:
            cursor.execute('''
                INSERT INTO users (user_id, user_name, user_class, user_classname, user_family_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, user_name, user_class, class_name, user_family_name))
            conn.commit()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        number = types.KeyboardButton("Raqamni jo'natish", request_contact=True)
        back = '🔙 Boshiga'
        markup.row(number, back)

        await message.reply("Iltimos raqamingizni jo'nating", reply_markup=markup)

    finally:
        # Close the SQLite connection in the finally block to ensure it is always closed
        conn.close()

# ...

# ...

# @dp.message_handler(content_types=types.ContentType.CONTACT)
# async def process_phone(message: types.Message):
#     user_id = message.from_user.id
#     user_name = user_data[user_id]["name"]
#     user_phone = message.contact.phone_number
#     user_family_name = user_data[user_id]["family_name"]
#     user_relation = user_data[user_id]["relation"]
#     scholl_number = user_data[user_id]['scholl_number']
#     user_class = user_data[user_id]["class"]
#     user_class_name = user_data[user_id]["class_name"]

#     await message.answer(
#         "Bergan ma'lumotlaringiz uchun rahmat tez orada sizga farzandingiz haqida ma'lumot berishni boshlaymiz")

#     # Initialize SQLite database connection
#     conn = sqlite3.connect('school_data.db')
#     cursor = conn.cursor()

#     try:
#         # Check if the user_id already exists in the users table
#         cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
#         existing_user = cursor.fetchone()

#         if existing_user:
#             # Update the existing record instead of inserting a new one
#             cursor.execute('''
#                 UPDATE users
#                 SET user_name=?, user_family_name=?, user_phone=?, user_relation=?, scholl_number=?, user_class=?, user_classname=?
#                 WHERE user_id=?
#             ''', (user_name, user_family_name, user_phone, user_relation, scholl_number, user_class, user_class_name, user_id))
#         else:
#             # Insert a new record
#             cursor.execute('''
#                 INSERT INTO users (user_id, user_name, user_family_name, user_phone, user_relation, scholl_number, user_class, user_classname)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#             ''', (user_id, user_name, user_family_name, user_phone, user_relation, scholl_number, user_class, user_class_name))

#         conn.commit()

#         user_data[user_id]["state"] = None
#         user_data[user_id]["relation"] = None

#     except sqlite3.Error as e:
#         print(f"SQLite error: {e}")
#         # Handle the error (log it, send a message to the user, etc.)

#     finally:
#         # Close the SQLite connection in the finally block to ensure it is always closed
#         conn.close()






if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
