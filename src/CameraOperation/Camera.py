import face_recognition
import subprocess


class VideoCamera(object):
    def __init__(self):
        self.action = False

    def get_action(self):
        return self.action

    def get_frame(self):
        picture_of_me = face_recognition.load_image_file("ja.jpeg")
        my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]

        for retries in range(3):
            subprocess.call(['streamer', '-t', '8', '-r', '3', '-o', 'frame00.jpeg'])

            for frame_number in range(5):
                unknown_picture = face_recognition.load_image_file(f"frame0{frame_number}.jpeg")
                try:
                    unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
                except IndexError:
                    continue

                results = face_recognition.compare_faces([my_face_encoding], unknown_face_encoding)

                if results[0]:
                    self.action = True
                    return True
        return False


if __name__ == '__main__':
    cam = VideoCamera()
    print(cam.get_frame())
