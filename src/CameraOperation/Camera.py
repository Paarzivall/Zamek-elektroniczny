"""
    Main module using to face recognize.
    Very simple because Raspberry Pi 3 can't working with streaming to website.
"""

import face_recognition
import subprocess


class VideoCamera(object):
    def __init__(self):
        self.action = False

    def get_action(self):
        """
            method to getting actual state of object in this class

        :return: class object
        :rtype: VideoCamera
        """
        return self.action

    def get_frame(self):
        """
        compare face from image with saving images("ja.png") from main folder location

        :return: True if face is rocognize or false if is not
        :rtype: bool
        """
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
