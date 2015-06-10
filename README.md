#[SickBeetz](http://www.sickbeetz.com)
##Generating Beats by Beatboxing
Authors: Corey Grief, Neal Kfoury, and Adam Snyder  
Northwestern Univeristy 
EECS 352  
Professor Bryan Pardo

###Overview
Analyzes recordings of humans beatboxing and transforms them into electronic drum beats. Does so by segmenting, classifying, quantizing, and replacing individual percussive 'notes' from a user-input audio stream. Written in Python 2.7 with the SciPy stack.

####Running the Program
The user may [visit SickBeetz on the web](http://www.sickbeetz.com), or can lauch SickBeetz from the command line:
```
python sickBeetz.py [path to audio file] [kit_#]
```
further installation instructions can be found at [The Wiki](https://github.com/cegrief/SickBeetz/wiki/SickBeetz-Wiki)

At the home screen, the user may press the record button and begin beatboxing into the system's microphone. They can then press the stop button when they are finished recording. Alternatively, they are able to upload an audio file for processing.

The interface will then prompt the user to select their preferred of three drum kits. The user may subsequently press the play button to hear the result or download it for later.

###Packages Used
####LibROSA
Used for various audio processing tasks such as onset detection, calculation of MFCCs and delta-MFCCs, and tempo estimation.
####PyAudio
Used for recording and saving audio input and output.
####scikit-learn
Used for building k-nearest neighbor classifier.
####Tkinter
Used for constructing graphical user interface.
