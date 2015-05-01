#SickBeetz
##Generating Beats by Beatboxing
Authors: Corey Grief, Neal Kfoury, and Adam Snyder  
Northwestern Univeristy 
EECS 352  
Professor Bryan Pardo

###Overview
Analyzes recordings of humans beatboxing and transforms them into electronic drum beats. Does so by segmenting, classifying, quantizing, and replacing individual percussive 'notes' from a user-input audio stream. Written in Python 2.7 with the SciPy stack.

####Running the Program
The user may lauch SickBeetz from the command line:
```
python sickBeetz.py [path to audio file] [kit_#]
```
At the home screen, the user may press the record button and begin beatboxing into the system's microphone. The user may press the stop button when the user is through.

The interface will then prompt the user to select their preferred of three drum kits, and provide the user with the option to quantize their beat to its estimated tempo. The user may subsequently press the play button to hear the result, which the user shall be able thereafter to find located in the SickBeetz directory under the name:
```
output.wav
```

###Packages Used
####LibROSA
Used for various audio processing tasks such as onset detection, calculation of MFCCs and delta-MFCCs, and tempo estimation.
####PyAudio
Used for recording and saving audio input and output.
####scikit-learn
Used for building k-nearest neighbor classifier.
####Tkinter
Used for constructing graphical user interface.
