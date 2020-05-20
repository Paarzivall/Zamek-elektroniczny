"""
Main method to analyze spreech frequency etc.
"""

import wave
import librosa.display
from dtw import dtw
from numpy.linalg import norm
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 32000
CHUNK = 960
RECORD_SECONDS = 3


class SpreechAnalyzer:
    OUTPUT_FILE = 'sounds/tmp.wav'

    def __init__(self):
        """
        initialize object to microphone management
        """
        self.audio = pyaudio.PyAudio()

    def recognize(self):
        """
        recording for 3 second and save sample as tmp.wav

        :return: method for checking valid sample
        :rtype: SpreechAnalyzer because this is method of this class
        """
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 2
        fs = 44100  # Record at 44100 samples per second
        seconds = 3

        print('Recording')

        stream = self.audio.open(format=sample_format,
                                 channels=channels,
                                 rate=fs,
                                 frames_per_buffer=chunk,
                                 input=True)
        frames = []

        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        self.audio.terminate()

        print('Finished recording')

        # Save the recorded data as a WAV file
        wf = wave.open(self.OUTPUT_FILE, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(self.audio.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        return self.controller()


    @staticmethod
    def controller():
        """
        method who checking voice samples

        :return: True if sample is valid or False if samle is not valid
        :rtype: bool
        """

        y1, sr1 = librosa.load('sounds/probka1.wav')
        y3, sr3 = librosa.load('sounds/probka2.wav')
        y4, sr4 = librosa.load('sounds/probka3.wav')
        y2, sr2 = librosa.load('sounds/tmp.wav')

        mfcc1 = librosa.feature.mfcc(y1, sr1)  # Computing MFCC values
        librosa.display.specshow(mfcc1)
        mfcc3 = librosa.feature.mfcc(y3, sr3)  # Computing MFCC values
        librosa.display.specshow(mfcc3)
        mfcc4 = librosa.feature.mfcc(y4, sr4)  # Computing MFCC values
        librosa.display.specshow(mfcc4)
        mfcc2 = librosa.feature.mfcc(y2, sr2)
        librosa.display.specshow(mfcc2)

        dist, cost, acc_cost, path = dtw(mfcc1.T, mfcc2.T, dist=lambda x, y: norm(x - y, ord=1))
        print("dist " + str(dist))
        if dist <= 25000:
            return True
        else:
            dist, cost, acc_cost, path = dtw(mfcc3.T, mfcc2.T, dist=lambda x, y: norm(x - y, ord=1))
            print("dist " + str(dist))
            if dist <= 25000:
                return True
            else:
                dist, cost, acc_cost, path = dtw(mfcc4.T, mfcc2.T, dist=lambda x, y: norm(x - y, ord=1))
                print("dist " + str(dist))
                if dist <= 25000:
                    return True
                else:
                    return False


if __name__ == '__main__':
    spreech = SpreechAnalyzer()
    if spreech.recognize() is True:
        print('speech verified')

    else:
        print('not verified')
