### Experimenting with KNN for n-dimensional arrays

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
import librosa
import os
import numpy as np
import matplotlib.pyplot as plt
import pickle

import segmentr
import sickBeetz

training_mfccs = [0, 1, 2, 4, 5]
num_mfccs = 20


def train_classifier(data, labels):
    model = KNeighborsClassifier()
    model.fit(data, labels)

    expected = labels
    predicted = model.predict(data)

    print classification_report(expected, predicted)
    print confusion_matrix(expected, predicted)

    return model


def use_classifier(classifier, seg, kit):
    p = classifier.predict(get_feature_from_mfcc(get_mfcc(seg, 44100)))
    # print "Sample: %s\nPrediction: %s" % (seg, p)
    return librosa.load('kits/'+kit+'/'+p[0]+'.wav', sr=None)


def main():
    model = load_classifier()


def load_pickle(filename):
    model_file = sickBeetz.relative_path(filename)
    if os.path.isfile(model_file):
        return pickle.load(open(model_file, 'rb'))
    return []


def save_pickle(object, filename):
    model_file = open(sickBeetz.relative_path(filename), 'wb')
    pickle.dump(object, model_file)
    model_file.close()


def load_classifier():
    samples = load_samples()
    features = []
    labels = []
    for sample, label, sr in samples:
        features.append(get_feature_from_mfcc(get_mfcc(sample, sr)))
        labels.append(label)
    model = train_classifier(features, labels)
    return model


def load_samples():
    result = load_pickle('samples.p')
    table_of_contents = load_pickle('toc.p')
    samples_dir = sickBeetz.relative_path('samples/unparsed-samples')
    for filename in os.listdir(samples_dir):
        if filename in table_of_contents:
            continue
        full_filename = sickBeetz.relative_path(os.path.join('samples/unparsed-samples', filename))
        if not os.path.isfile(full_filename):
            continue
        label_toks = filename.split('-')
        label = '-'.join(label_toks[i] for i in range(len(label_toks)-1))
        y, sr = librosa.load(full_filename, sr=None)

        segments = segmentr.segment_audio(y, sr)
        print filename + ' - ' + str(len(segments))
        for segment in segments:
            result.append((segment[0], label, sr))
        table_of_contents.append(filename)
    save_pickle(result, 'samples.p')
    save_pickle(table_of_contents, 'toc.p')
    return result


def get_mfcc(y, sr, plot=False):
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=64, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=num_mfccs)

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
    result = []
    for i in range(len(training_mfccs)):
        mfcc_i = mfcc[training_mfccs[i]]
        len_mfcc_i = np.size(mfcc_i)
        result.append(np.average(mfcc_i[0:len_mfcc_i/5]))
        result.append(np.average(mfcc_i[len_mfcc_i/5:]))
    return result


if __name__ == "__main__":
    main()