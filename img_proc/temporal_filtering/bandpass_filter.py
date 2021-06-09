import os, sys
import numpy as np

import mkl_fft._numpy_fft as mkl_fft

from scipy.ndimage import gaussian_filter1d

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def ideal_window(f, lowcut, highcut, allow_equal):
    """
    :param f: frequency points
    :param lowcut: bandpass filter low cut frequency
    :param highcut: bandpass filter high cut frequency
    :param allow_equal: include or exclude endpoints (lowcut, highcut)
    :return: ideal window (! not symmetrical in Fourier space !)
    """
    if allow_equal:
        return 1 if (f >= lowcut and f <= highcut) else 0
    else:
        return 1 if (f > lowcut and f < highcut) else 0


ideal_window_vectorized = np.vectorize(ideal_window, excluded=["lowcut", "highcut", "allow_equal"])


def ideal_bandpass_filter(N, fs, lowcut, highcut, allow_equal = True):
    """
    ]-N/2,-highcut[ = 0
    [-highcut,-lowcut] = 1
    ]-lowcut,lowcut[ = 0
    [lowcut,highcut] = 1
    ]highcut, N/2 [ = 0

    lowcut = "highpass" frequency
    highcut = "lowpass" frequency

    :param N: number of timepoints (samples) in signal
    :param fs: signal sampling frequency
    :param lowcut: low cut frequency of bandpass filter
    :param highcut: high cut frequency of bandpass filter
    :return: ideal bandpass filter defined in Fourier space (symmetrical)
    """

    _freqs = sorted([lowcut,highcut])
    lowcut, highcut = _freqs[0], _freqs[1]

    frequency_points = np.fft.fftfreq(N, 1 / fs)

    F_positive = ideal_window_vectorized(frequency_points,lowcut=lowcut, highcut = highcut, allow_equal=allow_equal)
    F_negative = ideal_window_vectorized(frequency_points,lowcut=-highcut, highcut = -lowcut, allow_equal=allow_equal)

    F = np.max([F_negative, F_positive], axis=0)

    return F

def smoothed_ideal_bandpass_filter(N, fs, lowcut, highcut, fwhm, allow_equal = True):
    """
    :param N: number of timepoints in signal
    :param fs: signal sampling frequency
    :param lowcut: low cut frequency of bandpass filter
    :param highcut: high cut frequency of bandpass filter
    :param fwhm: FWHM of gaussian used for smoothing an ideal bandpass filter [in Hz unit !!]
    :return: smoothed ideal bandpass filter defined in Fourier space (symmetrical)
    """
    _freqs = sorted([lowcut, highcut])
    lowcut, highcut = _freqs[0], _freqs[1]


    def fwhm2sigma(fwhm):
        return fwhm / np.sqrt(8 * np.log(2))

    frequency_resolution = fs / N

    #fwhm scaling, fwhm -> sigma conversion
    fwhm = float(fwhm) / float(frequency_resolution)
    sigma = fwhm2sigma(fwhm)

    frequency_points = np.fft.fftfreq(N, 1 / fs)
    frequency_points = np.fft.fftshift(frequency_points)

    F_positive = ideal_window_vectorized(frequency_points,lowcut=lowcut, highcut = highcut, allow_equal=allow_equal)
    smoothed_F_positive = gaussian_filter1d(F_positive.astype(float),sigma = sigma,mode = "constant", cval=0.0)

    F_negative = ideal_window_vectorized(frequency_points, lowcut=-highcut, highcut=-lowcut, allow_equal=allow_equal)
    smoothed_F_negative = gaussian_filter1d(F_negative.astype(float),sigma = sigma,mode = "constant", cval=0.0)

    smoothed_F = np.max([smoothed_F_positive, smoothed_F_negative], axis=0)

    smoothed_F = np.roll(smoothed_F,-np.argwhere(frequency_points==0.0)[0,0])

    return smoothed_F


def sigmoid_bandpass_filter(N, fs, lowcut, highcut, lowtail = 1, hightail = 1):
    """
    :param N: number of timepoints in signal
    :param fs: signal sampling frequency
    :param lowcut: low cut frequency of bandpass filter
    :param highcut: high cut frequency of bandpass filter
    :param lowtail: lower tail width controlling  (long tail: lowtail<1; normal tail: lowtail=1; short tail: lowtail>1)
    :param hightail: higher tail width controlling
    :return:
    """

    _freqs = sorted([lowcut, highcut])
    lowcut, highcut = _freqs[0], _freqs[1]

    frequency_resolution = fs / N
    niquist_frequency = fs / 2

    frequency_points = np.fft.fftfreq(N,1/fs)

    def sigmoid(x,a = 1, x0 = 0):
        if isinstance(x,np.ndarray):
            a = np.ones_like(x)*a
            x0 = np.ones_like(x)*x0

        return 1 / (1 + np.exp(-(a/frequency_resolution * (x - x0) )))

    def sigmoid_window(f, lowcut, highcut, lowtail, hightail):
        if lowcut != 0:
            val = sigmoid(f,lowtail,lowcut)
            if highcut!=0:
                return val - sigmoid(f,hightail,highcut)
            else:
                return val
        else:
            if highcut!=0:
                return 1 - sigmoid(f,hightail,highcut)
            else:
                return 1

    F_positive = sigmoid_window(frequency_points,lowcut=lowcut, highcut = highcut, lowtail = lowtail, hightail = hightail)
    F_negative = sigmoid_window(frequency_points,lowcut=-highcut, highcut = -lowcut, lowtail = hightail, hightail = lowtail)

    F = np.max([F_negative, F_positive], axis=0)

    return F


def plot_filter(filter, N, fs, lowcut, highcut, title= "", show_coordinates = False):
    """
    Visualizing a filter defined in Fourier-space
    """

    if not isinstance(filter,np.ndarray):
        raise TypeError

    if not filter.shape[0] == N:
        raise ValueError("Filter size not matches N")

    frequency_points = np.fft.fftfreq(N, 1 / fs)

    frequency_points = np.fft.fftshift(frequency_points)
    filter = np.fft.fftshift(filter)

    plt.plot(frequency_points,filter,color = "blue", linestyle = "dotted", alpha = 0.5)
    plt.plot(frequency_points,filter,color = "blue", linestyle = "None", marker = "+")

    inner_rect_width = lowcut*2
    orect_1 = mpatches.Rectangle((np.min(frequency_points), 0), abs(np.min(frequency_points)-(-highcut)), 1,  alpha=0.1, facecolor="red")
    irect_1 = mpatches.Rectangle((-lowcut, 0), inner_rect_width, 1,  alpha=0.1, facecolor="red")
    orect_2 = mpatches.Rectangle((highcut, 0), abs(np.max(frequency_points)-(highcut)), 1,  alpha=0.1, facecolor="red")
    plt.gca().add_patch(orect_1)
    plt.gca().add_patch(orect_2)
    plt.gca().add_patch(irect_1)

    if show_coordinates:
        if N%2 == 0:
            indices = np.arange(0,frequency_points.shape[0])
        else:
            indices = np.arange(0, frequency_points.shape[0], 2)
        for i in indices:
            x,y = frequency_points[i], filter[i]
            plt.text(x,y+.02, '({:.3f})'.format(x),fontsize = 4 + N%2*2, rotation = 90, alpha = 0.5, horizontalalignment = "center")

    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    plt.title(title)

    plt.show()


def bandpass_filtering(signal, filter):
    return np.real(np.fft.ifftn(np.fft.fftn(signal) * filter))


def mkl_bandpass_filtering(signal, filter):
    return np.real(mkl_fft.ifft(mkl_fft.fft(signal)*filter))


def bandpass_temportal_filtering_4d_image(image_data, filter, mask = None, mkl = True, dtype = np.float32):
    """
    :param image_data: 4D image data as ndarray
    :param filter: corresponding filter defined in Fourier space (symmetrical with -N//2 roll)
    :param mask: 3D image mask as ndarray
    :param mkl: allow mkl fft (faster computing on large scale data)
    :return: temporal bandpass filtered image
    """
    if not isinstance(image_data,np.ndarray):
        raise TypeError

    if not isinstance(filter,np.ndarray):
        raise TypeError

    mask_indices = False
    if isinstance(mask,np.ndarray):
        if image_data.shape[:3] == mask.shape:
            mask_indices = True

    if mask_indices:
        indices = np.argwhere(mask == 1)
        filtered_data = np.zeros_like(image_data, dtype = dtype)
        if mkl:
            for i in indices:
                filtered_data[tuple(i)] = mkl_bandpass_filtering(image_data[tuple(i)],filter)
        else:
            for i in indices:
                filtered_data[tuple(i)] = bandpass_filtering(image_data[tuple(i)], filter)

    else:
        if mkl:
            filtered_data = mkl_bandpass_filtering(image_data,filter)
        else:
            filtered_data = bandpass_filtering(image_data,filter)

    return filtered_data


if __name__ == '__main__':
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