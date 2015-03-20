import Tkinter
import threading
import Queue
import platform
import subprocess
import ttk
import pyaudio
import wave
import time

import sickBeetz


class SickBeetzGUI(ttk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.raise_and_focus()
        self.pack(fill=Tkinter.BOTH, expand=True)

        logo_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/sick_beetz_logo.gif'))
        logo_widget = Tkinter.Label(self, image=logo_img)
        logo_widget.photo = logo_img
        logo_widget.pack(side=Tkinter.TOP, fill=Tkinter.X)

        title_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/sick_title.gif'))
        title_widget = Tkinter.Label(self, image=title_img)
        title_widget.photo = title_img
        title_widget.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.status = StatusBar(self)
        self.status.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)

        self.window = Tkinter.Frame(self)
        self.window.configure(bg='white')
        self.window.pack(fill=Tkinter.BOTH, expand=True)

        self.queue = Queue.Queue()
        self.periodic_dequeue()

        self.record_state()

        # Misc globals
        self.rec_button = None
        self.finished_processing = False
        self.kit_selected = False

    def call_async(self, function, callback, *args):
        new_args = [function, callback]
        for arg in args:
            new_args.append(arg)
        threading.Thread(target=self.async_function, args=new_args).start()

    def async_function(self, function, callback, *args):
        function(*args)
        if callback:
            self.queue.put(callback)

    def periodic_dequeue(self):
        """
        Periodically checks for incoming asynchronous content so that the GUI will not freeze
        """
        while self.queue.qsize():
            try:
                self.queue.get(0)()
            except Queue.Empty:
                pass
        self.parent.after(100, self.periodic_dequeue)

    def record_state(self):
        self.clear_screen()

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=0)
        self.window.columnconfigure(2, weight=1)
        self.window.columnconfigure(3, weight=0)
        self.window.columnconfigure(4, weight=0)

        header_text = Tkinter.Label(self.window, text="Hello and welcome to SickBeetz, a program that will transform "
                                                      "your beatboxing into a polished drum beat.\nTo begin, click the "
                                                      "record button and begin beatboxing into your microphone.",
                                    wraplength=1000, justify=Tkinter.CENTER)
        header_text.grid(row=1, column=1, pady=20)

        rec_button = RecordButton(self.window, self)
        rec_button.grid(row=2, column=1)

        self.center_on_screen()

    def select_kit(self):
        self.clear_screen()
        self.status.set('Processing...')
        options = MutationOptions(self.window, self.parent)
        self.call_async(sickBeetz.quantize_and_classify, options.processing_finished, 'temp.wav')

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=0)
        self.window.columnconfigure(2, weight=0)
        self.window.columnconfigure(3, weight=0)
        self.window.columnconfigure(4, weight=1)

        header_text = Tkinter.Label(self.window, text="Choose your drum kit:",
                                    wraplength=1000, justify=Tkinter.CENTER)
        header_text.grid(row=1, column=1, columnspan=3, pady=20)

        standard_kit_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/standard_kit.gif'))
        standard_kit_button = Tkinter.Button(self.window, image=standard_kit_img,
                                             command=lambda: self.set_drum_kit('kit_2', standard_kit_button, button_list))
        standard_kit_button.photo = standard_kit_img
        standard_kit_button.grid(row=2, column=1)
        standard_txt = Tkinter.Label(self.window, text='Standard Kit')
        standard_txt.grid(row=3, column=1)

        bit_kit_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/8bit_kit.gif'))
        bit_kit_button = Tkinter.Button(self.window, image=bit_kit_img,
                                        command=lambda: self.set_drum_kit('kit_1', bit_kit_button, button_list))
        bit_kit_button.photo = bit_kit_img
        bit_kit_button.grid(row=2, column=2)
        bit_txt = Tkinter.Label(self.window, text='8-Bit Kit')
        bit_txt.grid(row=3, column=2)

        latin_kit_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/latin_kit.gif'))
        latin_kit_button = Tkinter.Button(self.window, image=latin_kit_img,
                                          command=lambda: self.set_drum_kit('kit_3', latin_kit_button, button_list))
        latin_kit_button.photo = latin_kit_img
        latin_kit_button.grid(row=2, column=3)
        latin_txt = Tkinter.Label(self.window, text='Latin Kit')
        latin_txt.grid(row=3, column=3)

        button_list = [standard_kit_button, bit_kit_button, latin_kit_button]

        quantize_text = Tkinter.Label(self.window, text="Would you like to quantize your input? This will track your "
                                                        "tempo and align your beats.", wraplength=1000,
                                      justify=Tkinter.CENTER)
        quantize_text.grid(row=4, column=1, columnspan=3)

        is_quantized = Tkinter.BooleanVar()

        c = Tkinter.Checkbutton(self.window, text="Quantize", variable=is_quantized)
        c.grid(row=5, column=1, columnspan=3)

        options.grid(row=6, column=1, columnspan=3)

        self.update()

    def set_drum_kit(self, kit, button, button_list):
        for b in button_list:
            b.config(state=Tkinter.NORMAL)
        self.kit_selected = kit
        button.config(state=Tkinter.DISABLED)

    def clear_screen(self):
        for widget in self.window.winfo_children():
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


class PlayAudioButton(Tkinter.Frame):

    def __init__(self, parent, gui):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.gui = gui
        self.stop_button_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/stop_button.gif'))
        self.play_button_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/play_button.gif'))
        self.button = Tkinter.Button(self)
        self.config(width=40, height=40)
        self.button.pack()
        self.ready()

    def ready(self):
        onsets = None
        quantized = None
        kit = None
        self.button.config(image=self.play_button_img,
                           command=lambda: self.gui.call_async(self.play_audio, None, onsets, quantized, kit))
        self.button.photo = self.play_button_img
        self.update()

    def play_audio(self, onsets, quantized, kit):
        pass


class StatusBar(ttk.Frame):
    """
    A custom widget that sits at the bottom of the GUI and displays program status updates
    """

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, relief=Tkinter.SUNKEN, anchor='w')
        self.label.pack(fill=Tkinter.X)

    def set(self, format0, *args):
        self.label.config(text=format0 % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text='')
        self.label.update_idletasks()


class MutationOptions(Tkinter.Frame):

    def __init__(self, parent, gui):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.gui = gui
        self.waiting_state()

    def waiting_state(self):
        label_1 = Tkinter.Label(self, text="Processing...")
        label_1.pack(pady=10)
        label_2 = Tkinter.Label(self, text="Your audio file is very important to us")
        label_2.pack()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def processing_finished(self):
        self.gui.status.set('Finished processing!')
        self.clear_screen()
        button = PlayAudioButton(self, self.gui)
        button.pack()


class RecordButton(Tkinter.Frame):

    def __init__(self, parent, gui):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.gui = gui
        self.rec_button_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/rec_button.gif'))
        self.stop_button_img = Tkinter.PhotoImage(file=sickBeetz.relative_path('img/stop_button.gif'))
        self.button = Tkinter.Button(self)
        self.config(width=40, height=40)
        self.button.pack()
        self.record_ready()
        self.is_recording = False

    def record_ready(self):
        self.button.config(image=self.rec_button_img,
                           command=lambda: self.gui.call_async(self.record_audio, self.gui.select_kit))
        self.button.photo = self.rec_button_img
        self.update()
        self.is_recording = False

    def record_audio(self):
        self.button.config(state=Tkinter.DISABLED)

        chunk = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 44100
        wave_output_filename = 'temp.wav'

        p = pyaudio.PyAudio()

        stream = p.open(format=audio_format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        frames = []

        self.is_recording = True
        self.gui.status.set('Getting silence...')
        really_going = False

        while self.is_recording:
            try:
                data = stream.read(chunk)
            except IOError:
                print 'Error - skipped buffer'
                continue
            frames.append(data)

            if not really_going and len(frames) > 0.5*rate/chunk:
                really_going = True
                self.button.config(image=self.stop_button_img, command=self.record_ready)
                self.button.photo = self.stop_button_img
                self.button.config(state=Tkinter.NORMAL)
                self.update()
                self.gui.status.set('Listening...')

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(wave_output_filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(audio_format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()


def main():
    root = Tkinter.Tk()
    root.title('Sick Beetz')
    root.geometry('1000x1000')
    app = SickBeetzGUI(root)
    root.mainloop()