# audio segmenter attempt using onset detection via librosa

import librosa


def segment_audio(signal, sr):
    o_env = librosa.onset.onset_strength(signal, sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr)
    print(onset_frames)
    print(onset_times)


def main():

    y, sr = librosa.load('samples/segmenter-tests/psh.wav')
    segment_audio(y, sr)


if __name__ == "__main__":
    main()