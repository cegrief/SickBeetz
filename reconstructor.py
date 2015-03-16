import numpy as np


# replaces each segment with its corresponding replacement, and returns the updated sound
def replace(times, replacements, sr, y):

    out = np.zeros(len(y))
    for i in range(0, len(replacements)):
        start = times[i]*sr
        end = start + len(replacements[i])
        for j in range(int(start), int(end)):
            out[j] += replacements[i][j-start]
    return out
