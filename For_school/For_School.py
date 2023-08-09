import cv2
import face_recognition
import datetime

def main():
    # Web kamerani yoqish
    video_capture = cv2.VideoCapture(0)

    # Tanilgan yuzning tasvirlari va nomlari
    known_face_encodings = []
    known_face_names = ["Muhammad","SherMuhammad"]  # Tanilgan yuzlarni nomlari

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

            # Tanilgan yuz bo'lsa va nom tanilmagan bo'lsa, vaqtni saqlash
            if name != "Unknown" and name not in recognized_names:
                now = datetime.datetime.now()
                formatted_time = now.strftime("%d-%B kuni soat: %H:%M:%S")
                with open("info.txt", "a") as f:
                    f.write(f"{name} : {formatted_time} maktab eshigidan kirdi\n")
                recognized_names.add(name)  # Nomni saqlash

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
