import numpy as np


def get_MNI_152(freesurfer_coords):
    v = np.array(freesurfer_coords)
    M = np.array(
        [
            [0.9975, -0.0073, 0.0176, -0.0429],
            [0.0146, 1.0009, -0.0024, 1.5496],
            [-0.0130, -0.0093, 0.9971, 1.1840],
        ]
    ).T
    return np.dot(v, M)


def location_details(x):
    # TODO: write function to get location details with NiMARE
    print(x)
