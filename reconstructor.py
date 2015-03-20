import numpy as np


# replaces each segment with its corresponding replacement, and returns the updated sound
def replace(times, replacements, sr):
    MAX_KIT_SOUND = 400000
    out = np.zeros(times[-1]*sr+MAX_KIT_SOUND)
    for i in range(0, len(replacements)):
        start = times[i]*sr
        end = start + len(replacements[i])
        for j in range(int(start), int(end)):
            out[j] += replacements[i][j-start]
    return out
