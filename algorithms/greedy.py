def greedy_windows(sequence, window_size):
    windows = []
    for i in range(len(sequence) - window_size + 1):
        windows.append(sequence[i:i + window_size])
    return windows