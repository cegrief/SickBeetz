import sys
import librosa
import segmentr
import klassifier
import reconstructor
import os

import sick_beetz_gui


def main(file_path, kit):
    y, sr = librosa.load(file_path, sr=None)
    segments = segmentr.segment_audio(y, sr)
    samples = [s[0] for s in segments]
    times = [s[1] for s in segments]

    # build the KNN classifier
    model = klassifier.load_classifier()
    replacements = []
    ssr = 0
    for seg in samples:
        sy, ssr = klassifier.use_classifier(model, seg, kit)
        replacements.append(sy)

    # quantize and reconstruct
    quantized_times = quantize_times(y, sr, times)
    output = reconstructor.replace(quantized_times, replacements, ssr)
    librosa.output.write_wav('output.wav', output, ssr)


def quantize_times(y, sr, times):
    result = []
    tempo = librosa.beat.beat_track(y, sr)[0]
    while tempo > 220:
        tempo = tempo/2
    while tempo < 90:
        tempo = tempo*2
    beet = 16/tempo
    first_time = times[0]
    for time in times:
        time = time - first_time
        time = beet*round(float(time)/beet)
        time = time + first_time
        result.append(time)
    return result


def quantize_and_classify(filename):
    # load and segment audio signal
    y, sr = librosa.load(filename, sr=None)
    segments = segmentr.segment_audio(y, sr)
    samples = [s[0] for s in segments]
    times = [s[1] for s in segments]

    # build and use KNN classifier
    model = klassifier.load_classifier()
    labels = []
    for seg in samples:
        label = klassifier.use_classifier(model, seg)
        labels.append(label)

   # quantize onset times to estimated tempo
    quantized_times = quantize_times(y, sr, times)

    return (times, quantized_times, labels)


def build_output(times, quantized_times, labels, kit, quantized=True):
    # check for empty arrays
    if not times or not labels:
        return False

    # replace beatbox with drums
    drums = []
    for label in labels:
        drum, ssr = librosa.load('kits/'+kit+'/'+label+'.wav', sr=None)
        drums.append(drum)

    # reconstruct signal from replaced sounds
    if quantized:
        result = reconstructor.replace(quantized_times, drums, ssr)
    else:
        result = reconstructor.replace(times, drums, ssr)

    # write output signal to .wav
    librosa.output.write_wav('output.wav', result, ssr)
    return True


def relative_path(path):
    """
    Get file path relative to calling script's directory
    :param path: filename or file path
    :return: full path name, relative to script location
    """
    return os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), path)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sick_beetz_gui.main()
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print 'usage: python sickBeetz [path_to_wav] [kit]'