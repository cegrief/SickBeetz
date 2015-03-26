# audio segmenter attempt using onset detection via librosa

import librosa
import sys
import matplotlib.pyplot as plt
import numpy as np
import math

HOP_LENGTH = 256
SILENCE_STEP = 2048
SILENCE_THRESHOLD = .5
MIN_SOUND_LEN = 0.02
START_TIME = 0.5
END_TIME = 0.1


def segment_audio(signal, sr):

    silence_threshold = get_silence_threshold(signal, sr)
    o_env = librosa.onset.onset_strength(y=signal, sr=sr, centering=False, hop_length=HOP_LENGTH)
    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr, hop_length=HOP_LENGTH)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=HOP_LENGTH)

    segments = []
    for i in range(len(onset_times)):
        segment_start = onset_times[i]*sr
        if i != len(onset_times)-1:
            segment_end = (onset_times[i+1]*sr)-HOP_LENGTH
        else:
            segment_end = len(signal)-1
        segment_end = find_segment_end(segment_start, segment_end, signal, silence_threshold)
        if (segment_end - segment_start >= MIN_SOUND_LEN*sr) and (onset_times[i] > START_TIME)\
                and (onset_times[i] < (len(signal)/sr-END_TIME)):
            segments.append((signal[segment_start: segment_end], onset_times[i]))
    return segments


def get_silence_threshold(signal, sr):
    silence_threshold = 2*rms(signal[sr/10:sr*START_TIME])
    print 'silence threshold: ' + str(silence_threshold)
    return silence_threshold


def find_segment_end(st, n, signal, silence_threshold):
    for i in xrange(int(st), int(n), SILENCE_STEP):
        if rms(signal[i:n]) < silence_threshold:
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