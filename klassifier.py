### Experimenting with KNN for n-dimensional arrays

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
import librosa
import os
import numpy as np
import matplotlib.pyplot as plt


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


def main_z():
    data = []
    labels = []
    dataset = open('training/dataset1.txt', 'r')
    for line in dataset:
        line.split(',')
        data.append(list(line[0]))
        labels += line[2]
    # print data, labels
    m = train_classifier(data, labels)
    use_classifier(m, 3.5)
    return


def main():
    samples = load_samples()
    features = []
    labels = []
    for sample in samples['ts']:
        features.append(get_mfcc(sample, 44100))
        labels.append('ts')
    # TODO: Pass to classifier


def load_samples():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    samples = {}
    # TODO: Fix file loading pathname bug
    for inst in ['b', 'ts', 'c']:
        foo = os.path.join(current_dir, 'samples', inst)
        samples[inst] = [f for f in os.listdir(foo) if os.path.isfile(os.path.join(foo, f))]
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

if __name__ == "__main__":
    main()