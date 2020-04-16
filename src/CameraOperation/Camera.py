import cv2
import face_recognition


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.action = False

    def __del__(self):
        self.video.release()

    def get_action(self):
        return self.action

    def get_frame(self):

        # dla wiekszej ilości twarzy dodawać kolejne linijki
        ja_image = face_recognition.load_image_file("../ja.jpg")
        ja_face_encoding = face_recognition.face_encodings(ja_image)[0]

        # durzucić też tutaj dla kolejnej twarzy
        known_face_encodings = [
            ja_face_encoding
        ]

        # i tutaj podpis opcjonalnie
        known_face_names = [
            "Mateusz"
        ]
        while True:
            # pobieram pojedyncze klatki
            ret, frame = self.video.read()

            # konwertuje z BGR na RGB
            # rgb_frame = frame[:, :, ::-1]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # szukam każdej twarzy
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # sprawdzam czy dana twarz jest znana
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    self.action = True
                # rysuje kwadrat naokoło twarzy
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # dodaje podpis do twarzy
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            ret, jpeg = cv2.imencode('.jpg', frame)

            return jpeg.tobytes()
