import cv2
import face_recognition
import os
import sqlite3
from datetime import datetime
import requests

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TELEGRAM_BOT_TOKEN = '6487765756:AAGwUvqglUMxsw0tVZ_DY29VRe_AQf-a4-s'

# Function to create a database and table if not exists
def create_database(database_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detected_faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            detected_time TEXT NOT NULL,
            exit_time TEXT
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

    connection.commit()
    connection.close()

# Function to copy data from school_data.db to {school_number}.db
def copy_school_data(school_number, new_database_path):
    school_data_connection = sqlite3.connect("school_data.db")
    school_data_cursor = school_data_connection.cursor()

    # Check if the school number exists in the school_data.db
    school_data_cursor.execute("SELECT * FROM users WHERE scholl_number=?", (school_number,))
    school_data = school_data_cursor.fetchone()

    school_data_connection.close()

    if school_data:
        new_connection = sqlite3.connect(new_database_path)
        new_cursor = new_connection.cursor()

        # Create the users table in the new database if not exists
        create_database(new_database_path)

        # Insert the data into the new database
        new_cursor.execute('''
            INSERT INTO users (
                user_id, user_name, user_phone, user_relation,
                user_class, user_classname, user_family_name, scholl_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', school_data)

        new_connection.commit()
        new_connection.close()

# Function to load known faces from the given directory
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

# Function to send a message using the Telegram Bot API
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
    }
    response = requests.post(url, params=params)
    return response.json()

# Function to insert detected face information into the database and send a Telegram message
def insert_detected_face(name, detected_time, database_path, school_data_db_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO detected_faces (name, detected_time)
        VALUES (?, ?)
    ''', (name, detected_time))

    connection.commit()

    # Retrieve user_id from school_data.db based on the detected face's name
    school_data_connection = sqlite3.connect(school_data_db_path)
    school_data_cursor = school_data_connection.cursor()

    school_data_cursor.execute("SELECT user_id FROM users WHERE user_name=?", (name,))

    user_id = school_data_cursor.fetchone()

    school_data_connection.close()

    connection.close()

# Function to update exit time in the database and send a Telegram message
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

# Load known faces and their names
path_to_known_faces = "path_to_known_faces"
known_face_encodings, known_face_names = load_known_faces(path_to_known_faces)

# Ask the user to enter the school number
school_number = input("Please enter the school number: ")

# Create a new database based on the entered school number
new_database_path = f"{school_number}.db"
create_database(new_database_path)

# Copy data from school_data.db to the new database
copy_school_data(school_number, new_database_path)

# Set to store recognized faces
recognized_faces = set()
exited_faces = set()

# Open camera
video_capture = cv2.VideoCapture(1)

# Main loop
while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Find all face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Check if the face matches any known face and has not been recognized before
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)


        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

            # Get the current date and time
            detected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time = datetime.now().strftime("%H:%M:%S")

            # Insert the detected face information into the new database and send a Telegram message
            if name not in recognized_faces:
                insert_detected_face(name, detected_time, new_database_path, "school_data.db")

                school_data_connection = sqlite3.connect("school_data.db")
                school_data_cursor = school_data_connection.cursor()
                school_data_cursor.execute("SELECT user_id FROM users WHERE user_name=?", (name,))

                user_id = school_data_cursor.fetchone()

                # Send a Telegram message for the entry time
                entry_message = f"Farzandingiz {name} Soat {time}da maktab eshigidan kirdi! "
                send_telegram_message(TELEGRAM_BOT_TOKEN, user_id[0], entry_message)

                recognized_faces.add(name)

        # Check if the face has already been recognized and update exit time
        elif name not in exited_faces:
            exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_exit_time(name, exit_time, new_database_path)

            school_data_connection = sqlite3.connect("school_data.db")
            school_data_cursor = school_data_connection.cursor()
            school_data_cursor.execute("SELECT user_id FROM users WHERE user_name=?", (name,))

            user_id = school_data_cursor.fetchone()

            # Send a Telegram message for the exit time
            exit_message = f"Farzandingiz {name} Soat {exit_time}da maktabdan chiqdi! "
            send_telegram_message(TELEGRAM_BOT_TOKEN, user_id[0], exit_message)

            exited_faces.add(name)

        # Draw rectangle and label on the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
video_capture.release()
cv2.destroyAllWindows()
