from .bandpass_filter import *


def bandpass_filter_shapes():
    N = 245

    dt = 2.59
    fs = 1/dt
    lowcut = 0.05
    highcut = 0.15

    ideal_filter = ideal_bandpass_filter(N,fs,lowcut,highcut)
    plot_filter(ideal_filter, N, fs, lowcut, highcut, title = "Ideal bandpass filter")

    smoothed_filter = smoothed_ideal_bandpass_filter(N,fs,lowcut,highcut, 0.005)
    plot_filter(smoothed_filter, N, fs, lowcut, highcut, title = "Smoothed ideal bandpass filter")

    sigmoid_filter = sigmoid_bandpass_filter(N,fs,lowcut,highcut,5,2)
    plot_filter(sigmoid_filter,N,fs,lowcut,highcut, title = "Sigmoid bandpass filter")


if __name__ == '__main__':
    bandpass_filter_shapes()