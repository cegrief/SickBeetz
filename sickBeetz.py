import numpy
import sys
import librosa
import segmentr
import klassifier
import reconstructor
import os
import timeit
#import sick_beetz_gui


def main(file_path, kit):
    time, quantized, labels = quantize_and_classify(file_path, klassifier.load_classifier(), False)
    print build_output(time, quantized, labels, kit, file_path, False)

def timeMain(filename, kit):
    start_time = timeit.default_timer()
    y,sr = librosa.load(filename, sr=None)
    print("librosa.load: ")
    print(timeit.default_timer() - start_time)

    start_time = timeit.default_timer()
    segments = segmentr.segment_audio(y, sr)
    print("segmenter: ")
    print(timeit.default_timer() - start_time)

    start_time = timeit.default_timer()
    model = klassifier.load_classifier()
    print("Load Klassifier: ")
    print(timeit.default_timer() - start_time)

    samples = [s[0] for s in segments]
    times = [s[1] for s in segments]
    labels = []
    i = 1
    start_time = timeit.default_timer()
    for seg in samples:
        label = klassifier.use_classifier(model, seg)
        labels.append(label)
        i += 1

    print("all classifications: ")
    print(timeit.default_timer() - start_time)

    start_time = timeit.default_timer()
    quantized_times = quantize_times(y, sr, times)
    print("Quantize_times: ")
    print(timeit.default_timer() - start_time)


def quantize_times(y, sr, times):
    result = []
    if not times:
        return result
    tempo = librosa.beat.beat_track(y, sr)[0]
    while tempo > 220:
        tempo /= 2
    while tempo < 90:
        tempo *= 2
    beet = 16/tempo
    first_time = times[0]
    for time in times:
        time = time - first_time
        time = beet*round(float(time)/beet)
        time = time + first_time
        result.append(time)
    return result


def quantize_and_classify(filename, model, quantized=False):
    # load and segment audio signal
    y, sr = librosa.load(filename, sr=None)
    segments = segmentr.segment_audio(y, sr)
    samples = [s[0] for s in segments]
    times = [s[1] for s in segments]
    labels = []
    for seg in samples:
        label = klassifier.use_classifier(model, seg)
        labels.append(label)

    # quantize onset times to estimated tempo
    if quantized:
        quantized_times = quantize_times(y, sr, times)
    else:
        quantized_times = times

    return (times, quantized_times, labels)


def build_output(times, quantized_times, labels, kit, file_path, quantized=False):
    # check for empty arrays
    if not times or not labels:
        return False
    labels = [label[0] for label in labels]
    # replace beatbox with drums
    drums = []
    label_to_kit = {}
    for label in labels:
        if label in label_to_kit:
            drum = label_to_kit[label]
        else:
            drum, ssr = librosa.load('../kits/'+kit+'/'+label+'.wav', sr=None)
            label_to_kit[label] = drum
        drums.append(drum)

    # reconstruct signal from replaced sounds
    if quantized:
        result = reconstructor.replace(quantized_times, drums, ssr)
    else:
        result = reconstructor.replace(times, drums, ssr)

    # write output signal to .wav
    librosa.output.write_wav(file_path[:-4]+'-out.wav', result, ssr)
    return result, ssr


def relative_path(path):
    """
    Get file path relative to calling script's directory
    :param path: filename or file path
    :return: full path name, relative to script location
    """
    return os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), path)


if __name__ == "__main__":
    # if len(sys.argv) == 1:
    #     #sick_beetz_gui.main()
    # el
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        timeMain(sys.argv[1], sys.argv[2])
    else:
        print 'usage: python sickBeetz [path_to_wav] [kit]'