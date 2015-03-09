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

kit = 'kit_2'


def train_classifier(data, labels):
    model = KNeighborsClassifier()
    model.fit(data, labels)

    expected = labels
    predicted = model.predict(data)

    print classification_report(expected, predicted)
    print confusion_matrix(expected, predicted)

    return model


def use_classifier(classifier, sample):
    p = classifier.predict(sample)
    print "Sample: %s\nPrediction: %s" % (sample, p)
    return


def main():
    model = load_classifier()
    new_sample = listen_for_speech()
    play_wav(new_sample)
    new_features = get_feature_from_mfcc(get_mfcc(new_sample, 44100))
    use_classifier(model, new_features)


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


def load_classifier():
    samples = load_samples()
    features = []
    labels = []
    for sample in samples['ts']:
        features.append(get_feature_from_mfcc(get_mfcc(sample, 44100)))
        labels.append('ts')
    for sample in samples['b']:
        features.append(get_feature_from_mfcc(get_mfcc(sample, 44100)))
        labels.append('b')
    for sample in samples['c']:
        features.append(get_feature_from_mfcc(get_mfcc(sample, 44100)))
        labels.append('c')
    model = train_classifier(features, labels)
    return model


def load_samples():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    samples = {}
    # TODO: Fix file loading pathname bug
    for inst in ['b', 'ts', 'c']:
        foo = os.path.join(current_dir, 'samples', inst)
        samples[inst] = [os.path.abspath('samples/'+inst+'/'+f)
                         for f in os.listdir(foo) if os.path.isfile(os.path.join(foo, f))]
    return samples


def get_mfcc(filename, sr, plot=False):
    y, sr = librosa.load(filename, sr)
    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=2048, hop_length=64, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=20)

    if plot:
        plt.figure(figsize=(12,4))
        librosa.display.specshow(log_S, sr=sr, hop_length=64, x_axis='time', y_axis='mel')
        plt.title('mel power spectrogram')
        plt.colorbar(format='%+02.0f dB')

        plt.figure(figsize=(12, 6))
        plt.subplot(3,1,1)
        librosa.display.specshow(mfcc)
        plt.ylabel('MFCC')
        plt.colorbar()
        plt.subplot(3,1,2)
        plt.show()
    return mfcc


def get_feature_from_mfcc(mfcc):
    return np.sum(mfcc, axis=1)


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