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


def extract_roi_name(term):
    """Extract the ROI name from a Neurosynth term.

    Parameters
    ----------
    term : str
        Neurosynth term.

    Returns
    -------
    roi_name : str
        ROI name.
    """
    return term.split("__")[1]


def location_details(roi, atlas_img, out_dir, method="association", n_labels=1, decoder=None):
    """Get details about a ROI.

    Parameters
    ----------
    roi : str
        Index of the ROI in the atlas.
    atlas_img : nib.Nifti1Image
        Atlas image.
    out_dir : str
        Output directory.
    method : str, optional
        Decoding method, by default "association"
    n_labels : int, optional
        Number of labels to retrieve (between 1 and 5), by default 1

    Raises
    ------
    ValueError
        If the method is not supported.

    Returns
    -------
    roi_names : list
        List of ROI names.

    Notes
    -----

    Based on the following link in the NiMare docs: https://bit.ly/3nH7hWF
    """
    atlas = atlas_img.get_fdata()
    roi_mask = atlas.copy()
    roi_mask[roi_mask != roi] = 0
    roi_mask[roi_mask == roi] = 1
    roi_img = new_img_like(atlas_img, roi_mask)

    # Get dataset from neurosynth if it doesn't exist.
    if not os.path.exists(os.path.join(out_dir, "neurosynth_dataset.pkl.gz")):
        dset = neurosynth_to_nimare(out_dir)
        dset.save(os.path.join(out_dir, "neurosynth_dataset.pkl.gz"))
    else:
        dset = Dataset.load(os.path.join(out_dir, "neurosynth_dataset.pkl.gz"))

    # Decode the ROI.
    if method == "brainmap" or method == "chi":
        # Get studies with voxels in the mask
        ids = dset.get_studies_by_mask(roi_img)

        # Initialize decoder
        if decoder is None and method == " brainmap":
            decoder = discrete.BrainMapDecoder(correction=None)
        elif decoder is None and method == "chi":
            decoder = discrete.NeurosynthDecoder(correction=None)
        elif decoder is None:
            raise ValueError("Method not supported.")

        decoder.fit(dset)
        decoded_df = decoder.transform(ids=ids)
        top_results = decoded_df.sort_values(by="probReverse", ascending=False).head()

    elif method == "association":
        # Neurosynth ROI association method
        # This method decodes the ROI image directly
        decoder = discrete.ROIAssociationDecoder(roi_img)
        decoder.fit(dset)

        # The `transform` method doesn't take any parameters.
        decoded_df = decoder.transform()

        # Sort by `r` of association
        top_results = decoded_df.sort_values(by="r", ascending=False).head()
    else:
        raise ValueError(f"Method {method} not supported.")

    # Get the top n_labels labels
    roi_names = [extract_roi_name(x) for x in top_results.index[:n_labels]]

    # Return the name of the n_labels ROIs with the highest score
    return roi_names, decoder


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
