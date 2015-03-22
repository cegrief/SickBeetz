import numpy as np


# replaces each segment with its corresponding replacement, and returns the updated sound
def replace(times, replacements, sr):
    out = initialize_output(times, replacements, sr)
    for i in range(0, len(replacements)):
        start = times[i]*sr
        end = start + len(replacements[i])
        for j in range(int(start), int(end)):
            out[j] += replacements[i][j-start]
    return out


def initialize_output(times, replacements, sr):
    end_times = [len(times)]
    for i in range(len(times)):
        end_times[i] = sr*times[i] + len(replacements[i])
    return np.zeros(max(end_times)+1)