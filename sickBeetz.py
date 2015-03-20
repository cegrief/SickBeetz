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
import subprocess
import Queue
import threading
import time
import os


class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.raise_and_focus()
        self.pack(fill=Tkinter.BOTH, expand=True)
        self.splash_state()
        self.queue = Queue.Queue()
        threading.Thread(target=self.start_timer, args=[3, 1]).start()
        self.periodic_dequeue()

    def start_timer(self, seconds, num):
        """
        Waits for a specified number of seconds. Meant to be run asynchronously.
        """
        time.sleep(seconds)
        self.queue.put(num)

    def periodic_dequeue(self):
        """
        Periodically checks for incoming asynchronous content so that the GUI will not freeze
        """
        while self.queue.qsize():
            try:
                function = self.queue.get(0)
                if function == 1:
                    self.first_state()
            except Queue.Empty:
                pass
        self.parent.after(100, self.periodic_dequeue)

    def splash_state(self):
        splash_image_file = Tkinter.PhotoImage(file=relative_path('sick_splash.gif'))
        splash_image_widget = Tkinter.Label(self, image=splash_image_file)
        splash_image_widget.photo = splash_image_file
        splash_image_widget.pack()
        self.center_on_screen()

    def onClick(self, text, kit):
        self.second_state()
        self.update()
        if text:
            path = text
        else:
            path = 'samples/segmenter-tests/test1.wav'

        if kit:
            thekit = kit
        else:
            thekit = 'kit_2'

        y, sr = librosa.load(path, sr=None)
        segments = segmentr.segment_audio(y, sr)
        samples = [s[0] for s in segments]
        times = [s[1] for s in segments]

        # build the KNN classifier
        model = klassifier.load_classifier()
        replacements = []
        ssr = 0
        for seg in samples:
            sy, ssr = klassifier.use_classifier(model, seg, thekit)
            replacements.append(sy)

        output = reconstructor.replace(times, replacements, ssr)
        librosa.output.write_wav('output.wav', output, ssr)
        self.third_state()
        self.update()

    def pickFile(self, tb):
        filename = askopenfilename()
        tb.insert(0, filename)

    def first_state(self):
        self.clear_screen()
        self.parent.geometry("500x150+300+300")
        self.center_on_screen()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, pad=10)
        self.pack_configure(padx=10, pady=10)

        url_label = ttk.Label(self, text="Enter a path to an audio file:")
        url_label.grid(columnspan=3, sticky=Tkinter.W)

        url_text_box = ttk.Entry(self, width=50)
        url_text_box.grid(row=1, sticky=Tkinter.E+Tkinter.W+Tkinter.S+Tkinter.N)

        choose_button = ttk.Button(self, text="choose an audio file", command=lambda: self.pickFile(url_text_box))
        choose_button.grid(row=1, column=2)

        v = Tkinter.StringVar()

        ok_button = ttk.Button(self, text="OK", command=lambda: self.onClick(url_text_box.get(), v.get()))
        ok_button.grid(row=1, column=3)

        r1 = ttk.Radiobutton(self, text="Standard Kit", variable=v, value='kit_2')
        r1.grid(row=3, column=3)
        r2 = ttk.Radiobutton(self, text="8-bit Kit", variable=v, value='kit_1')
        r2.grid(row=4, column=3)
        r3 = ttk.Radiobutton(self, text="Latin Kit", variable=v, value='kit_3')
        r3.grid(row=5, column=3)

        v.set('kit_2')

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
        threading.Thread(target=self.start_timer, args=[2, 1]).start()


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
    root.title('Sick Beetz')
    app = Example(root)
    root.mainloop()


def relative_path(path):
    """
    Get file path relative to calling script's directory
    :param path: filename or file path
    :return: full path name, relative to script location
    """
    return os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), path)


if __name__ == "__main__":
    main(sys.argv[1:])