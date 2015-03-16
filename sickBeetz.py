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

    if len(argv) > 1 and argv[1] in ['kit_1', 'kit_2', 'kit_3']:
        kit = argv[1]
    else:
        print 'Incorrect drum kit arg format; assuming \'kit_1\''
        kit = 'kit_1'
    print path
    y, sr = librosa.load(path, sr=None)
    segments, times = segmentr.segment_audio(y, sr)

    # build the KNN classifier
    model = klassifier.load_classifier()
    replacements = []
    ssr = 0
    for seg in segments:
        sy, ssr = klassifier.use_classifier(model, seg, kit)
        replacements.append(sy)

    output = reconstructor.replace(times, replacements, ssr, y)
    librosa.output.write_wav('output.wav', output, ssr)



if __name__ == "__main__":
    main(sys.argv[1:])