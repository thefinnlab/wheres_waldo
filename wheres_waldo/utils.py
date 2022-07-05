import os

import numpy as np
from nilearn.image import new_img_like
from nimare.dataset import Dataset
from nimare.decode import discrete
from nimare.extract import fetch_neurosynth
from nimare.io import convert_neurosynth_to_dataset
from nimare.utils import get_resource_path


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


def location_details(roi, atlas_img, method="association"):
    """_summary_

    Parameters
    ----------
    roi : str
        Index of the ROI in the atlas.
    atlas_img : nib.Nifti1Image
        Atlas image.
    method : str, optional
        Decoding method, by default "association"

    Raises
    ------
    ValueError
        If the method is not supported.

    Returns
    -------
    _type_
        _description_

    Notes
    -----

    Based on the following link: https://bit.ly/3nH7hWF
    """
    atlas = atlas_img.get_fdata()
    roi_mask = atlas.copy()
    roi_mask[roi_mask != roi] = 0
    roi_mask[roi_mask == roi] = 1
    roi_img = new_img_like(atlas_img, roi_mask)

    # Load dataset with abstracts
    dset = Dataset(os.path.join(get_resource_path(), "neurosynth_laird_studies.json"))
    dset.annotations.head(5)

    if method == "brainmap" or method == "chi":
        # Get studies with voxels in the mask
        ids = dset.get_studies_by_mask(roi_img)

    elif method == "association":
        # Neurosynth ROI association method
        # This method decodes the ROI image directly
        decoder = discrete.ROIAssociationDecoder(roi_img)
        decoder.fit(dset)

        # The `transform` method doesn't take any parameters.
        decoded_df = decoder.transform()

        decoded_df.sort_values(by="r", ascending=False).head()
    else:
        raise ValueError(f"Method {method} not supported.")


def neurosynth_to_nimare(out_dir, source="abstract", vocab="terms"):
    """Download Neurosynth data and convert to nimare dataset.

    Parameters
    ----------
    out_dir : str
        Output directory.
    source : str, optional
        Source of the data, by default "abstract"
    vocab : str, optional
        Vocabulary to use, by default "terms"

    Returns
    -------
    neurosynth_dataset : nimare.dataset.Dataset
        Neurosynth dataset.
    """
    out_dir = os.path.abspath("../example_data/")
    os.makedirs(out_dir, exist_ok=True)

    files = fetch_neurosynth(
        data_dir=out_dir,
        version="7",
        overwrite=False,
        source=source,
        vocab=vocab,
    )
    # Note that the files are saved to a new folder within "out_dir" named "neurosynth".
    neurosynth_db = files[0]

    neurosynth_dset = convert_neurosynth_to_dataset(
        coordinates_file=neurosynth_db["coordinates"],
        metadata_file=neurosynth_db["metadata"],
        annotations_files=neurosynth_db["features"],
    )
    # neurosynth_dset.save(os.path.join(out_dir, "neurosynth_dataset.pkl.gz"))

    return neurosynth_dset
