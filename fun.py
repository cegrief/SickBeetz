import pyaudio
import wave
import platform
import os
from Tkinter import *
from collections import deque
import math
import audioop
import time
import librosa
import numpy as np
import matplotlib.pyplot as plt

# and IPython.display for audio output
import IPython.display


class Fun:
    def __init__(self):

        self.start_stream()
        # self.is_recording = False
        # self.rec_button = None
        # self.root = Tk()
        # self.root.title("Fun")
        # self.init_widgets()
        # self.center_on_screen()
        # self.raise_and_focus()
        # self.root.mainloop()

    def init_widgets(self):
        self.rec_button = Button(self.root, text="Record", command=self.rec)
        self.rec_button.pack()

    def raise_and_focus(self):
        self.root.call('wm', 'attributes', '.', '-topmost', '1')
        if platform.system() == 'Darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

    def center_on_screen(self):
        self.root.geometry("+%d+%d" % (
            (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) / 2,
            (self.root.winfo_screenheight() - self.root.winfo_reqheight()) / 3
        ))
        self.root.deiconify()

    def rec(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.rec_button['text'] = 'Stop'
            self.start_stream()
        else:
            self.rec_button['text'] = 'Record'
            self.end_stream()

    def start_stream(self):
        while True:
            self.listen_for_speech()
        pass

    def end_stream(self):
        pass

    def listen_for_speech(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        SILENCE_LIMIT = 0.5
        PREV_AUDIO = 0.5
        THRESHOLD = 800
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print "* Listening mic. "
        audio2send = []
        rel = RATE/CHUNK
        slid_win = deque(maxlen=SILENCE_LIMIT * rel)
        prev_audio = deque(maxlen=PREV_AUDIO * rel)
        started = False
        response = []
        finished = False

        while not finished:
            cur_data = stream.read(CHUNK)
            slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
            if sum([x > THRESHOLD for x in slid_win]) > 0:
                if not started:
                    print "Starting"
                    started = True
                audio2send.append(cur_data)
            elif started:
                print "Finished"
                filename = self.save_speech(list(prev_audio) + audio2send, p)
                r = self.process(filename)
                print "Response:", r
                os.remove(filename)
                started = False
                slid_win = deque(maxlen=SILENCE_LIMIT * rel)
                prev_audio = deque(maxlen=0.5 * rel)
                audio2send = []
                finished = True
            else:
                prev_audio.append(cur_data)
        stream.close()
        p.terminate()

        return response

    def save_speech(self, data, p):
        filename = 'output_'+str(int(time.time()))
        # writes data to WAV file
        data = ''.join(data)
        wf = wave.open(filename + '.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)  # TODO make this value a function parameter?
        wf.writeframes(data)
        wf.close()
        return filename + '.wav'

    def process(self, filename):
        y, sr = librosa.load(filename, 16000)

        # Let's make and display a mel-scaled power (energy-squared) spectrogram
        # We use a small hop length of 64 here so that the frames line up with the beat tracker example below.
        S = librosa.feature.melspectrogram(y, sr=sr, n_fft=2048, hop_length=64, n_mels=128)

        # Convert to log scale (dB). We'll use the peak power as reference.
        log_S = librosa.logamplitude(S, ref_power=np.max)

        # Make a new figure
        plt.figure(figsize=(12,4))

        # Display the spectrogram on a mel scale
        # sample rate and hop length parameters are used to render the time axis
        librosa.display.specshow(log_S, sr=sr, hop_length=64, x_axis='time', y_axis='mel')

        # Put a descriptive title on the plot
        plt.title('mel power spectrogram')

        # draw a color bar
        plt.colorbar(format='%+02.0f dB')

        # Make the figure layout compact
        # plt.tight_layout()


        # Next, we'll extract the top 20 Mel-frequency cepstral coefficients (MFCCs)
        mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=20)

        # Let's pad on the first and second deltas while we're at it
        delta_mfcc  = librosa.feature.delta(mfcc)
        delta2_mfcc = librosa.feature.delta(mfcc, order=2)

        # How do they look?  We'll show each in its own subplot
        plt.figure(figsize=(12, 6))

        plt.subplot(3,1,1)
        librosa.display.specshow(mfcc)
        plt.ylabel('MFCC')
        plt.colorbar()

        plt.subplot(3,1,2)
        librosa.display.specshow(delta_mfcc)
        plt.ylabel('MFCC-$\Delta$')
        plt.colorbar()

        plt.subplot(3,1,3)
        librosa.display.specshow(delta2_mfcc, sr=sr, hop_length=64, x_axis='time')
        plt.ylabel('MFCC-$\Delta^2$')
        plt.colorbar()

        #plt.tight_layout()

        # For future use, we'll stack these together into one matrix
        M = np.vstack([mfcc, delta_mfcc, delta2_mfcc])
        plt.show()
        return mfcc

Fun()