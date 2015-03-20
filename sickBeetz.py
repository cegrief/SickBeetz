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

    output = reconstructor.replace(times, replacements, ssr)
    librosa.output.write_wav('output.wav', output, ssr)


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