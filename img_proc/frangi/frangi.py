import numpy as np

from .utils import divide_nonzero
from .hessian import absolute_hessian_eigenvalues


def frangi_3d(nd_array, scale_range=(1, 10), scale_step=2, alpha=0.5, beta=0.5, black_vessels=True, verbose = False,
              mask_nd_array = None, fwhm_scale = False, voxel_sizes = None, max_filter = True):

    if not nd_array.ndim == 3:
        raise(ValueError("Only 3 dimensions is currently supported"))

    # from https://github.com/scikit-image/scikit-image/blob/master/skimage/filters/_frangi.py#L74
    sigmas = np.arange(scale_range[0], scale_range[1], scale_step)

    if fwhm_scale:
        sigmas = sigmas/2.355 #FWHM to sigma conversion

    if np.any(np.asarray(sigmas) < 0.0):
        raise ValueError("Sigma values less than zero are not valid")

    filtered_array = np.zeros(nd_array.shape + sigmas.shape)

    for i, sigma in enumerate(sigmas):
        _sigma=sigma
        if isinstance(voxel_sizes, tuple):
            #transform to real-world scale
            _sigma = _sigma * np.ones(len(voxel_sizes))
            _sigma = _sigma/np.array(voxel_sizes)

        if verbose:
            print("Computing Frangi-filter with sigma value of {0} [FWHM={1}], scaled sigma value of {2}".format(sigma,sigma*2.355,_sigma))

        eigenvalues = absolute_hessian_eigenvalues(nd_array, sigma=_sigma, scale=True)

        frangi_c = compute_frangi_c(eigenvalues,mask_nd_array)
        if verbose:
            print("Frangi c value is {0}".format(frangi_c))

        filtered_array[:,:,:,i] = compute_vesselness(*eigenvalues, alpha=alpha, beta=beta, c=frangi_c,
                                               black_white=black_vessels)
    if max_filter:
        return np.max(filtered_array, axis=3)
    else:
        return filtered_array


def compute_frangi_c(eigenvalues,mask_nd_array = None):
    if len(eigenvalues)!=3:
        raise ValueError
    E1,E2,E3 = eigenvalues[0],eigenvalues[1],eigenvalues[2]


    if isinstance(mask_nd_array,np.ndarray):
        E = np.sqrt(E1**2+E2**2+E3**2)/2.0
        return np.max(E[mask_nd_array])
    else:
        return np.max(np.sqrt(E1**2+E2**2+E3**2))/2.0


def compute_measures(eigen1, eigen2, eigen3):
    """
    RA - plate-like structures
    RB - blob-like structures
    S - background
    """
    Ra = divide_nonzero(np.abs(eigen2), np.abs(eigen3))
    Rb = divide_nonzero(np.abs(eigen1), np.sqrt(np.abs(np.multiply(eigen2, eigen3))))
    S = np.sqrt(np.square(eigen1) + np.square(eigen2) + np.square(eigen3))
    return Ra, Rb, S


def compute_plate_like_factor(Ra, alpha):
    return 1 - np.exp(np.negative(np.square(Ra)) / (2 * np.square(alpha)))


def compute_blob_like_factor(Rb, beta):
    return np.exp(np.negative(np.square(Rb) / (2 * np.square(beta))))


def compute_background_factor(S, c):
    return 1 - np.exp(np.negative(np.square(S)) / (2 * np.square(c)))


def compute_vesselness(eigen1, eigen2, eigen3, alpha, beta, c, black_white):
    Ra, Rb, S = compute_measures(eigen1, eigen2, eigen3)
    plate = compute_plate_like_factor(Ra, alpha)
    blob = compute_blob_like_factor(Rb, beta)
    background = compute_background_factor(S, c)

    # return plate*blob
    return filter_out_background(plate * blob * background, black_white, eigen2, eigen3)


def filter_out_background(voxel_data, black_white, eigen2, eigen3):
    """
    Set black_white to true if vessels are darker than the background and to false if
    vessels are brighter than the background.
    """
    if black_white:
        voxel_data[eigen2 < 0] = 0
        voxel_data[eigen3 < 0] = 0
    else:
        voxel_data[eigen2 > 0] = 0
        voxel_data[eigen3 > 0] = 0
    voxel_data[np.isnan(voxel_data)] = 0
    return voxel_data
