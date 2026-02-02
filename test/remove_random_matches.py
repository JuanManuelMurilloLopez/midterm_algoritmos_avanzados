import random

def remove_random_matches(matches, k):
    indices = sorted(random.sample(range(len(matches)), k), reverse=True)
    m = matches[:]
    for i in indices:
        m.pop(i)
    return m
