# audio segmenter attempt using onset detection via librosa

import librosa
import sys
import matplotlib.pyplot as plt
import numpy as np
import math
import timeit

HOP_LENGTH = 256
SILENCE_STEP = 8192
SILENCE_WINDOW = 2048
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

def segment_audio_timeit(signal, sr):

    start_time = timeit.default_timer()
    silence_threshold = get_silence_threshold(signal, sr)
    print("getsilencethreshold: ")
    print(timeit.default_timer() - start_time)

    start_time = timeit.default_timer()
    o_env = librosa.onset.onset_strength(y=signal, sr=sr, centering=False, hop_length=HOP_LENGTH)
    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr, hop_length=HOP_LENGTH)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=HOP_LENGTH)
    print("librosa.onset_detect: ")
    print(timeit.default_timer() - start_time)

    segments = []

    overalltime = timeit.default_timer()
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

    print('all segments')
    print(timeit.default_timer() - overalltime)

    return segments

def get_silence_threshold(signal, sr):
    silence_threshold = 2*rms(signal[sr/10:sr*START_TIME])
    print 'silence threshold: ' + str(silence_threshold)
    return silence_threshold


def find_segment_end(st, n, signal, silence_threshold):
    for i in xrange(int(st), int(n), SILENCE_STEP):
        if rms(signal[i:i+SILENCE_WINDOW]) < silence_threshold:
            return i
    return n


def rms(y):
    x = sum([i**2 for i in y])/len(y)
    return math.sqrt(x)


def main(argv):

    if len(argv)==2:
        path = argv[0]
        disp = argv[1]
    elif len(argv)==1:
        path = argv[0]
        disp = False
    else:
        path = 'samples/beats/beat-1.wav'
        disp = True
    y, sr = librosa.load(path, sr=None)
    segments = segment_audio_timeit(y, sr)

    if disp:
        for i in range(0, len(segments)):
            print 'plotting segment: '+str(1+i)+' at time: '+str(segments[i][1])
            print 'num frames: '+str(len(segments[i][0]))
            starttime = segments[i][1]
            endtime = len(segments[i][0])/float(sr) + starttime
            time = np.linspace(starttime, endtime, num=len(segments[i][0]))
            plt.plot(time, segments[i][0])
            plt.title('Segment '+str(i+1))
            plt.xlabel('time(s)')
            plt.ylabel('amplitude')
            plt.grid(True)
            plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])