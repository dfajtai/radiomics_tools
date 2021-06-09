import os, sys
import numpy as np
import nibabel as nb
from nipype.utils.filemanip import filename_to_list, list_to_filename, split_filename

def ideal_bandpass_filter_image(files, lowpass_freq, highpass_freq, fs):
    """Bandpass filter the input files
    Parameters
    ----------
    files: list of 4d nifti files
    lowpass_freq: cutoff frequency for the low pass filter (in Hz)
    highpass_freq: cutoff frequency for the high pass filter (in Hz)
    fs: sampling rate (in Hz)
    """

    out_files = []
    for filename in filename_to_list(files):
        path, name, ext = split_filename(filename)
        out_file = os.path.join(os.getcwd(), name + '_bp' + ext)
        img = nb.load(filename)
        timepoints = img.shape[-1]
        F = np.zeros((timepoints))
        lowidx = timepoints//2 + 1
        if lowpass_freq > 0:
            lowidx = int(np.round(float(lowpass_freq) / fs * timepoints))
        highidx = 0
        if highpass_freq > 0:
            highidx = int(np.round(float(highpass_freq) / fs * timepoints))
        F[lowidx:highidx] = 1
        F = ((F + F[::-1]) > 0).astype(int)
        data = img.get_data()
        if np.all(F == 1):
            filtered_data = data
        else:
            X, Y, Z, T = img.shape
            for x in range(X):
                for y in range(Y):
                    for z in range(Z):
                        data[x,y,z] = np.real(np.fft.ifftn(np.fft.fftn(data[x,y,z]) * F))
            filtered_data = data
        img_out = nb.Nifti1Image(filtered_data, img.get_affine(),
                                 img.get_header())
        img_out.to_filename(out_file)
        out_files.append(out_file)
    return list_to_filename(out_files)



if __name__=='__main__':
    print("System 64bit: ")
    print(sys.maxsize > 2**32)

    in_file = sys.argv[1]
    img = nb.load(in_file)
    print(img.shape)
    fs = 1 / img.header['pixdim'][4]
    fqlow  = 0.08
    # fqhigh = 0.009
    fqhigh = 0.01

    out_file = ideal_bandpass_filter_image(in_file, fqlow, fqhigh, fs)
    print(out_file)
