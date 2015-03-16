import sys
import librosa
import segmentr
import klassifier
import reconstructor

def main(argv):

    if argv:
        path = argv[0]
    else:
        path = 'samples/segmenter-tests/test1.wav'

    y, sr = librosa.load(path, sr=None)
    segments, times = segmentr.segment_audio(y, sr)

    replacements = []
    for i in segments:
        #replacements.append(klassifier.klassify_segment(i))
        #just do kit_1 ts.wav for now
        sy, ssr = librosa.load('kits/kit_1/ts.wav', sr=None)
        replacements.append((sy, ssr))

    signal = reconstructor.replace(times, replacements, segments, y, sr)
    librosa.output.write_wav('output.wav', signal, sr)



if __name__ == "__main__":
    main(sys.argv[1:])