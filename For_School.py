import cv2
import face_recognition
import os
import sqlite3
from datetime import datetime, timedelta
import requests
from win10toast import ToastNotifier 


toaster = ToastNotifier()

TELEGRAM_BOT_TOKEN = '6438847465:AAHdcXrn7sKkDvYgCqsINkRfVOqdgUfWzSA'


def create_database(database_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detected_faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            detected_time TEXT NOT NULL,
            exit_time TEXT,
            user_class TEXT,
            user_classname TEXT
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers_data (
            user_id INTEGER PRIMARY KEY,
            teacher_name TEXT,
            teacher_phone TEXT,
            teacher_class TEXT,
            teacher_class_name TEXT,
            school_number TEXT,
            pass TEXT
        )
    ''')

    connection.commit()
    connection.close()

def copy_school_data(school_number, new_database_path):
    school_data_connection = sqlite3.connect("school_data.db")
    school_data_cursor = school_data_connection.cursor()

    # Select only the rows where school_number matches the input
    school_data_cursor.execute("SELECT * FROM users WHERE scholl_number=?", (school_number,))
    school_data_rows = school_data_cursor.fetchall()

    # Also select data from the teachers table where school_number matches
    school_data_cursor.execute("SELECT * FROM teachers WHERE school_number=?", (school_number,))
    teacher_data_rows = school_data_cursor.fetchall()

    school_data_connection.close()

    if school_data_rows:
        new_connection = sqlite3.connect(new_database_path)
        new_cursor = new_connection.cursor()

        create_database(new_database_path)

        # Insert each matching row from users table into the new database
        for row in school_data_rows:
            print(row)
            new_cursor.execute('''
                INSERT INTO users (
                    user_id, user_name, user_phone, user_relation, user_class, user_classname,  user_family_name, scholl_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', row)  # Exclude the last element from the row



        # Insert each matching row from teachers_data table into the new database
        for row_teacher in teacher_data_rows:
            print(row_teacher)
            new_cursor.execute('''
                INSERT INTO teachers_data (
                    user_id, teacher_name, teacher_phone, teacher_class, teacher_class_name, school_number, pass
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', row_teacher)

        new_connection.commit()
        new_connection.close()


def load_known_faces(known_faces_dir):
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(known_faces_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(known_faces_dir, filename)
            face_image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(face_image)[0]
            known_face_encodings.append(face_encoding)
            known_face_names.append(os.path.splitext(filename)[0])

    return known_face_encodings, known_face_names

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
    }
    response = requests.post(url, params=params)
    return response.json()

def insert_detected_face(name, detected_time, database_path, school_data_db_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO detected_faces (name, detected_time, user_class, user_classname)
        SELECT ?, ?, user_class, user_classname
        FROM users
        WHERE user_name = ?
    ''', (name, detected_time, name))

    connection.commit()
    connection.close()

    school_data_connection = sqlite3.connect(school_data_db_path)
    school_data_cursor = school_data_connection.cursor()

    school_data_cursor.execute("SELECT user_id FROM users WHERE user_name=?", (name,))

    user_id = school_data_cursor.fetchone()

    school_data_connection.close()

def update_exit_time(name, exit_time, database_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute('''
        UPDATE detected_faces
        SET exit_time = ?
        WHERE name = ? AND exit_time IS NULL
    ''', (exit_time, name))

    connection.commit()
    connection.close()

def enough_time_passed(entry_time, current_time, threshold_minutes=5):
    entry_datetime = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
    current_datetime = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    time_difference = current_datetime - entry_datetime
    return time_difference >= timedelta(minutes=threshold_minutes)

path_to_known_faces = "path_to_known_faces/"
known_face_encodings, known_face_names = load_known_faces(path_to_known_faces)

school_number = input("Please enter the school number: ")

new_database_path = f"{school_number}.db"
create_database(new_database_path)

copy_school_data(school_number, new_database_path)

recognized_faces = set()
exited_faces = set()
detected_times = {}

video_capture = cv2.VideoCapture(1)

name = ""  # Initialize 'name' outside the loop

while True:
    ret, frame = video_capture.read()

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        if True in matches:
            first_match_index = matches.index(True)
            detected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time = datetime.now().strftime("%H:%M:%S")
            name = known_face_names[first_match_index]

            if name not in recognized_faces:
                insert_detected_face(name, detected_time, new_database_path, "school_data.db")
                detected_times[name] = detected_time

                school_data_connection = sqlite3.connect("school_data.db")
                school_data_cursor = school_data_connection.cursor()
                school_data_cursor.execute("SELECT user_id FROM users WHERE user_name=?", (name,))

                user_id = school_data_cursor.fetchone()

                if user_id is not None and name != "Unknown":
                    entry_message = f"Farzandingiz {name} Soat {time}da maktab eshigidan kirdi! "
                    send_telegram_message(TELEGRAM_BOT_TOKEN, user_id[0], entry_message)

                    toaster.show_toast("Face Detected", f"{name} is detected!", duration=10)


                recognized_faces.add(name)

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()


        # Check if the face has already been recognized and update exit time
        # elif name not in exited_faces and name != "Unknown":
        #     exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #     # Check if enough time has passed for sending an exit message
        #     entry_time = detected_times.get(name, "")
        #     if entry_time and enough_time_passed(entry_time, exit_time):
        #         update_exit_time(name, exit_time, new_database_path)

        #         school_data_connection = sqlite3.connect("school_data.db")
        #         school_data_cursor = school_data_connection.cursor()
        #         school_data_cursor.execute("SELECT user_id FROM users WHERE user_name=?", (name,))

        #         user_id = school_data_cursor.fetchone()

        #         # Send a Telegram message for the exit time
        #         exit_message = f"Farzandingiz {name} Soat {exit_time}da maktabdan chiqdi! "
        #         send_telegram_message(TELEGRAM_BOT_TOKEN, user_id[0], exit_message)

        #         exited_faces.add(name)

        # Draw rectangle and label on the face

