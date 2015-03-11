### Experimenting with KNN for n-dimensional arrays

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
import librosa
import os
import numpy as np
import matplotlib.pyplot as plt
import audioop
import pyaudio
from collections import deque
import math
import time
import wave

import klassifier

kit = 'kit_2'


def main():
    model = klassifier.load_classifier()
    new_sample = listen_for_speech()
    play_wav(new_sample)
    new_features = klassifier.get_feature_from_mfcc(klassifier.get_mfcc(new_sample, 44100))
    print new_features
    klassifier.use_classifier(model, new_features)


def get_sound_threshold():
    print 'Reading silence. Shhhh.'
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    cur_data = stream.read(CHUNK)
    result = math.sqrt(abs(audioop.avg(cur_data, 4)))
    return result*4


def listen_for_speech():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    SILENCE_LIMIT = 0.2
    PREV_AUDIO = 0.2
    THRESHOLD = get_sound_threshold()
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print "* Microphone is listening *"
    audio2send = []
    rel = RATE/CHUNK
    slid_win = deque(maxlen=SILENCE_LIMIT * rel)
    prev_audio = deque(maxlen=PREV_AUDIO * rel)
    started = False
    finished = False

    while not finished:
        cur_data = stream.read(CHUNK)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        if sum([x > THRESHOLD for x in slid_win]) > 0:
            if not started:
                print "Starting"
                started = True
            audio2send.append(cur_data)
        elif started:
            print "Finished"
            filename = save_speech(list(prev_audio) + audio2send, p, RATE)
            stream.close()
            p.terminate()
            return filename
        else:
            prev_audio.append(cur_data)


def save_speech(data, p, sr):
    filename = 'output_'+str(int(time.time()))
    data = ''.join(data)
    wf = wave.open(filename + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sr)
    wf.writeframes(data)
    wf.close()
    return filename + '.wav'


def play_wav(f):
    chunk = 1024
    f = wave.open(f)
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    data = f.readframes(chunk)
    while data != '':
        stream.write(data)
        data = f.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()