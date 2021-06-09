
import os, sys
import numpy as np
import pandas as pd

from Std_Tools import read_image
from Std_Tools import extendable_file as ex
from Std_Tools.common.py_io import py_move

from scipy.signal import butter, lfilter, sosfilt, buttord
import matplotlib.pyplot as plt
from scipy.signal import freqz
import scipy.fftpack

from Std_Tools.visualization.plots.spectrum import plotSpectrum

from ideal_bandpass_filter_orig import ideal_bandpass_filter_image as bp_filter_numpy



def buttord_example():
    from scipy import signal
    import matplotlib.pyplot as plt

    # N, Wn = signal.buttord([20, 50], [14, 60], 3, 40, True)
    # b, a = signal.butter(N, Wn, 'band', True)
    # w, h = signal.freqs(b, a, np.logspace(1, 2, 500))

    N, Wn = signal.buttord([0.01, 0.08], [0.005, 0.085], 3, 40, True)
    b, a = signal.butter(N, Wn, 'band', True)
    w, h = signal.freqs(b, a, np.logspace(0.001, 1, 10))
    # w, h = signal.freqz(b, a, worN=2000)

    plt.semilogx(w, 20 * np.log10(abs(h)))
    # plt.plot(w, 20 * np.log10(abs(h)))

    plt.title('Butterworth bandpass filter fit to constraints')
    plt.xlabel('Frequency [radians / second]')
    plt.ylabel('Amplitude [dB]')
    plt.grid(which='both', axis='both')
    plt.fill([1,  14,  14,   1], [-40, -40, 99, 99], '0.9', lw=0) # stop
    plt.fill([20, 20,  50,  50], [-99, -3, -3, -99], '0.9', lw=0) # pass
    plt.fill([60, 60, 1e9, 1e9], [99, -40, -40, 99], '0.9', lw=0) # stop
    plt.axis([10, 100, -60, 3])
    plt.show()


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def sos_butter_bandpass(data, lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], btype='band',output="sos")
    y = sosfilt(sos,data)
    return y


def butter_bandpass_design(low_cut, high_cut, fs, d = 0.005, max_loss = 5, min_suppress = 60):
    from scipy import signal

    nyq = 0.5 * fs
    low = low_cut / nyq
    high = high_cut / nyq
    D = d / nyq

    N, Wn = signal.buttord([low, high], [low-D, high + D ], max_loss, min_suppress, True)
    print(f"The order of the analog Butterworth bandpass filter with given characteristics is {N}.")
    b, a = signal.butter(N, Wn, 'band', True)

    return b, a


def butter_bandpass_design_filter(data,low_cut, high_cut, fs, d = 0.005, max_loss = 5, min_suppress = 60):
    b,a = butter_bandpass_design(low_cut, high_cut, fs, d = d, max_loss = max_loss, min_suppress = min_suppress)
    y = lfilter(b, a, data)
    return y


def butter_filter_charasteristics_plot(fs = 1.0/2.59, lowcut = 0.01, highcut = 0.08):
    """
    :param fs: sample rate
    :param lowcut:
    :param highcut:
    :return:
    """

    # Plot the frequency response for a few different orders.

    fig, ax = plt.subplots(3, 1, figsize=(12, 10))

    # for order in [3, 6, 9, 12, 15]:
    for order in range(1,10,2):
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        w, h = freqz(b, a, worN=2000) #frequency response the filter

        ax[0].plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

        ax[1].plot((fs * 0.5 / np.pi) * w, 20 * np.log10(abs(h)), label="order = %d" % order)

        ax[2].plot((fs * 0.5 / np.pi) * w, np.unwrap(np.angle(h)) * 180 / np.pi, label="order = %d" % order)

    ax[0].plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
             '--', label='sqrt(0.5)')
    plt.xlabel('Frequency (Hz)')
    ax[0].set_title("Frequency Response")
    ax[0].set_ylabel('Gain')
    ax[0].grid(True)
    ax[0].legend(loc='best')

    ax[1].set_ylabel("Amplitude (dB)", color='blue')
    ax[1].grid(True)
    ax[1].legend(loc='best')

    ax[2].set_ylabel("Angle (degrees)", color='green')
    ax[2].set_yticks([-180, -150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150, 180])
    ax[2].set_ylim([-180, 180])
    ax[2].grid(True)
    ax[2].legend(loc='best')

    plt.show()

def test_butterworth_filters_on_signal(signal, time_scale, low_cut,high_cut,fs,orders):
    fig, ax = plt.subplots(2, 2, figsize=(12, 10))
    ax[0,0].plot(time_scale,signal)
    ax[0,0].set_ylabel("BOLD signal")
    ax[0,0].set_xlabel("Time [s]")

    # plotSpectrum(time_scale,signal,2000)

    N = signal.shape[0] #number of sample points
    T = 1.0/fs
    yf = scipy.fftpack.fft(signal)
    xf = np.linspace(0.0, 1.0 / (2.0 * T), (N // 2))

    print(np.allclose(scipy.fftpack.fft(scipy.fftpack.ifft(signal)), signal, atol=1e-15))

    ax[0,1].plot(xf, 20 * np.log10(np.abs(yf[:N // 2])))
    ax[0, 1].set_xlabel("Frequency [Hz]")
    ax[0, 1].set_ylabel("Amplitude [dB]")

    for order in orders:
        filtered_signal = butter_bandpass_filter(signal, lowcut=low_cut, highcut=high_cut, fs=fs, order=order)
        ax[1,0].plot(time_scale, filtered_signal, label="order = %d" % order)

        _yf = scipy.fftpack.fft(filtered_signal)
        ax[1, 1].plot(xf, 20 * np.log10(np.abs(_yf[:N // 2])), label="order = %d" % order)

        print(np.allclose(scipy.fftpack.fft(scipy.fftpack.ifft(filtered_signal)), filtered_signal, atol=1e-15))

    ax[1,0].set_ylabel("BOLD signal (filtered)")
    ax[1,0].set_xlabel("Time [s]")
    ax[1,0].legend(loc='upper right')
    ax[1,0].grid(True)

    ax[1, 1].set_ylabel("Amplitude [dB] of filtered signal")
    ax[1, 1].set_xlabel("Frequency [Hz]")
    ax[1, 1].legend(loc='upper right')
    ax[1, 1].grid(True)

    plt.show()



if __name__ == '__main__':
    # buttord_example()
    # filter_plot()
    pass

