import librosa
import os
import numpy as np
import matplotlib.pyplot as plt


def main():
    compute_histograms(20)


def compute_histograms(num_mfccs):
    samples = load_samples()
    b_data = get_mfcc_data(samples['b'], num_mfccs)
    ts_data = get_mfcc_data(samples['ts'], num_mfccs)
    c_data = get_mfcc_data(samples['c'], num_mfccs)
    for i in range(num_mfccs):
        f, axarr = plt.subplots(3, sharex=True)
        axarr[0].hist(b_data[i], facecolor='blue')
        axarr[0].set_title('b ['+str(i)+']')
        axarr[1].hist(ts_data[i], facecolor='green')
        axarr[1].set_title('ts ['+str(i)+']')
        axarr[2].hist(c_data[i], facecolor='red')
        axarr[2].set_title('c ['+str(i)+']')
        plt.show()


def get_mfcc_data(samples, num_mfccs):
    result = [None]*num_mfccs
    for i in range(num_mfccs):
        result[i] = []
    for sample in samples:
        mfcc = get_mfcc(sample, 44100, num_mfccs)
        for i in range(num_mfccs):
            result[i] = np.concatenate((result[i], mfcc[i]), axis=0)
    return result


def load_samples():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    samples = {}
    for inst in ['b', 'ts', 'c']:
        foo = os.path.join(current_dir, 'samples', inst)
        samples[inst] = [os.path.abspath('samples/'+inst+'/'+f)
                         for f in os.listdir(foo) if os.path.isfile(os.path.join(foo, f))]
    return samples


def get_mfcc(filename, sr, num_mfccs):
    y, sr = librosa.load(filename, sr)
    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=2048, hop_length=64, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=num_mfccs)
    return mfcc


if __name__ == "__main__":
    main()