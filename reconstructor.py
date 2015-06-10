import numpy as np


# replaces each segment with its corresponding replacement, and returns the updated sound
def replace(times, replacements, sr, inputLength):
    out = initialize_output(times, replacements, sr, inputLength)
    for i in range(0, len(replacements)):
        start = times[i]*sr
        end = start + len(replacements[i])
        for j in range(int(start), int(end)):
            out[j] += replacements[i][j-start]

    if len(out) > inputLength:
        return out[0:inputLength]
    else:
        return out


# initializes the output array.
# The array is either the length of the original audio file or the end time after the final replacement sound
def initialize_output(times, replacements, sr, inputLength):
    end_times = []
    for i in range(len(times)):
        end_times.append(sr*times[i] + len(replacements[i]))
    end_times.append(inputLength)
    return np.zeros(max(end_times)+1)