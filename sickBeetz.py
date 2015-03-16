import sys
import librosa
import segmentr
import klassifier
import reconstructor
import Tkinter
from Tkinter import Tk, Frame, BOTH
import ttk
import platform
from tkFileDialog import askopenfilename

class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.raise_and_focus()
        self.center_on_screen()
        self.first_state()
    

    def onClick(self, text):
    #     if len(argv) > 1 and argv[1] in ['kit_1', 'kit_2', 'kit_3']:
    #     kit = argv[1]
    # else:
    #     print 'Incorrect drum kit arg format; assuming \'kit_1\''
    #     kit = 'kit_1'
    # print path
    # y, sr = librosa.load(path, sr=None)
    # segments, times = segmentr.segment_audio(y, sr)
        self.second_state()
        self.update()
        if text:
            path = text
        else:
            path = 'samples/segmenter-tests/test1.wav'
    # build the KNN classifier
    # model = klassifier.load_classifier()
    # replacements = []
    # ssr = 0
    # for seg in segments:
    #     sy, ssr = klassifier.use_classifier(model, seg, kit)
    #     replacements.append(sy)

        y, sr = librosa.load(path, sr=None)
        segments, times = segmentr.segment_audio(y, sr)

        replacements = []
        for i in segments:
            #replacements.append(klassifier.klassify_segment(i))
            #just do kit_1 ts.wav for now
            sy, ssr = librosa.load('kits/kit_1/ts.wav', sr=None)
            replacements.append(sy)

        output = reconstructor.replace(times, replacements, ssr, y)
        librosa.output.write_wav('output.wav', output, ssr)
        self.third_state()
        self.update()

    def pickFile(self, tb):
        filename = askopenfilename()
        tb.insert(0,filename)

    def first_state(self):

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, pad=10)
        self.pack_configure(padx=10, pady=10)

        url_label = ttk.Label(self, text="Enter a path to an audio file:")
        url_label.grid(columnspan=3, sticky=Tkinter.W)

        url_text_box = ttk.Entry(self, width=50)
        url_text_box.grid(row=1, sticky=Tkinter.E+Tkinter.W+Tkinter.S+Tkinter.N)

        choose_button = ttk.Button(self, text="choose an audio file", command=lambda: self.pickFile(url_text_box))
        choose_button.grid(row=1, column=2)

        ok_button = ttk.Button(self, text="OK", command=lambda: self.onClick(url_text_box.get()))
        ok_button.grid(row=1, column=3)

    def second_state(self):
        self.clear_screen()
        url_label = ttk.Label(self, text="Processing...")
        url_label.pack()
        url_labe2l = ttk.Label(self, text="Your audio file is very important to us")
        url_labe2l.pack()

    def third_state(self):
        self.clear_screen()
        url_label = ttk.Label(self, text="Processing Complete! Your audio file is saved in output.wav")
        url_label.pack()


    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def raise_and_focus(self):
        # window.lift()
        self.parent.call('wm', 'attributes', '.', '-topmost', '1')
        if platform.system() == 'Darwin':
            try:
                subprocess.call(['/usr/bin/osascript', '-e',
                                 'tell app "System Events" to set frontmost of process "Python" to true'])
            except OSError:
                pass
        self.parent.deiconify()

    def center_on_screen(self):
        self.update_idletasks()
        w = self.parent.winfo_screenwidth()
        h = self.parent.winfo_screenheight()
        rootsize = tuple(int(_) for _ in self.parent.geometry().split('+')[0].split('x'))
        x = (w - rootsize[0]) / 2
        y = (h - rootsize[1]) / 3
        self.parent.geometry("%dx%d+%d+%d" % (rootsize + (x, y)))

def main(argv):

    root = Tk()
    root.geometry("500x100+300+300")
    app = Example(root)
    root.mainloop()



if __name__ == "__main__":
    main(sys.argv[1:])