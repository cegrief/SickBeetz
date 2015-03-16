# audio segmenter attempt using onset detection via librosa

import librosa
import sys
import matplotlib.pyplot as plt
import numpy as np
import math

HOP_LENGTH = 256
SILENCE_STEP = 2048
SILENCE_THRESHOLD = .5


def segment_audio(signal, sr):

    o_env = librosa.onset.onset_strength(y=signal[1000:len(signal)-1000], sr=sr, centering=False, hop_length=HOP_LENGTH)
    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr, hop_length=HOP_LENGTH)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=HOP_LENGTH)

    segments = []
    for i in range(0, len(onset_times)):
        segment_start = onset_times[i]*sr
        if i != len(onset_times)-1:
            segment_end = find_segment_end(segment_start, (onset_times[i+1]*sr)-1, signal)
        else:
            segment_end = find_segment_end(segment_start, len(signal)-1, signal)
        if segment_end - segment_start >= 512:
            segments.append(signal[segment_start: segment_end])
    return segments, onset_times


def find_segment_end(st, n, signal):
    for i in xrange(int(st), int(n), SILENCE_STEP):
        if rms(signal[i:n]) < SILENCE_THRESHOLD:
            return i
    return n


def rms(y):
    x = sum([i**2 for i in y])
    return math.sqrt(x)


def main(argv):

    if argv:
        path = argv[0]
    else:
        path = 'samples/segmenter-tests/test1.wav'
    y, sr = librosa.load(path, sr=None)
    segments, times = segment_audio(y, sr)

    for i in range(0, len(segments)):
        print 'plotting segment: '+str(1+i)+' at time: '+str(times[i])
        starttime = times[i]
        endtime = len(segments[i])/float(sr) + times[i]
        time = np.linspace(starttime, endtime, num=len(segments[i]))
        plt.plot(time, segments[i])
        plt.title('Segment '+str(i+1))
        plt.xlabel('time(s)')
        plt.ylabel('amplitude')
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])