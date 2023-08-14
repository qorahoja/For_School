import cv2
import face_recognition
import datetime
import requests
import csv
import collections



def send_info_to_telegram_bot(message, chat_id):
    bot_token = "6013857528:AAGH9iV9PI8WEg2-TCkNpxLOtWqSDQHgCmM"

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(api_url, params=params)
    if response.status_code == 200:
        print("Ma'lumotlar muvaffaqiyatli yuborildi!")
    else:
        print("Xatolik yuz berdi. Ma'lumotlar yuborilmadi!")


def read_chat_ids_from_csv(file_path):
    file_path = "users_data.csv"
    user_chat_ids = collections.defaultdict(list)
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            user_name, chat_id = row[0], row[2]  # Foydalanuvchi ID va chat ID ni olish
            user_chat_ids[user_name].append(chat_id)
    return user_chat_ids



def main():
            # Web kamerani yoqish
            video_capture = cv2.VideoCapture(0)

            # Tanilgan yuzning tasvirlari va nomlari
            known_face_encodings = []
            known_face_names = ["Muhammad", "SHermukhammad", "Umidyor"]  # Tanilgan yuzlarni nomlari

            user_chat_ids = collections.defaultdict(list)

            for name in known_face_names:
                known_image = face_recognition.load_image_file(f"path_to_known_faces/{name}.jpg")
                face_encoding = face_recognition.face_encodings(known_image)[0]
                known_face_encodings.append(face_encoding)
                # print(known_image, face_encoding, known_face_encodings)

            recognized_names = set()  # Tanilgan yuzlarni saqlash uchun hoshiya
            while True:
                # Kamera orqali tasvir olish
                ret, frame = video_capture.read()

                # Kameradan olingan tasvirdagi yuzlarni aniqlash
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                # print(face_encodings, face_locations)
                # Aniqlangan yuzlarni nomlarni saqlash uchun ro'yxat
                face_names = []
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]
                    face_names.append(name)


                    user_ids = []
                    with open('users_data.csv', 'r') as csvfile:
                        csv_reader = csv.reader(csvfile)
                        for row in csv_reader:
                            user_ids.append(row[2])

                    chat_ids = read_chat_ids_from_csv('users_data.csv')  # Foydalanuvchi chat ID-larini o'qib olamiz
                    chat_ids = chat_ids.get(name, [])  # Foydalanuvchi nomiga mos chat ID lar

                    if name != "Unknown" and chat_ids:  # Foydalanuvchi chat ID lari mavjud bo'lsa
                        if name not in recognized_names:  # Tanidik foydalanuvchini bir marotaba jo'natishni ta'minlash
                            now = datetime.datetime.now()
                            formatted_time = now.strftime("%d-%B kuni soat: %H:%M:%S")
                            message = f"{name} : {formatted_time} maktab eshigidan kirdi"
                            for chat_id in chat_ids:
                                send_info_to_telegram_bot(message, chat_id)  # Har bir chat ID ga xabar yuboramiz
                            recognized_names.add(name)  # Tanidik foydalanuvchi nomini saqlash

                # Yuzlarni doiralar bilan belgilash
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)


                # Tasvirni chiqarish
                cv2.imshow('Video', frame)

                # 'q' tugmasi bosilganda dastur to'xtatiladi
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Kamera yopiladi
            video_capture.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
            main()

