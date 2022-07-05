import argparse
import sys

import nibabel as nib
import pandas as pd
from nilearn.datasets import fetch_atlas_schaefer_2018

from wheres_waldo import __version__
from wheres_waldo.utils import get_MNI_152, location_details


def _get_parser():
    """
    Parse command line inputs for this function.

    Returns
    -------
    parser.parse_args() : argparse dict

    Notes
    -----
    # Argument parser follow template provided by RalphyZ.
    # https://stackoverflow.com/a/43456577
    """
    parser = argparse.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group("Required Arguments:")

    # Required arguments
    required.add_argument(
        "-r",
        "--rois",
        help="List of ROIs to be analyzed.",
        required=True,
        type=int,
        nargs="+",
        dest="rois",
    )
    required.add_argument(
        "-o",
        "--output",
        help="Output file name.",
        required=True,
        type=str,
        dest="output",
    )
    # Optional arguments
    optional.add_argument(
        "-d",
        "--dir",
        help="Directory to save the output files.",
        type=str,
        dest="out_dir",
        default=".",
    )
    optional.add_argument(
        "-n",
        "--networks",
        help="Number of networks to use.",
        required=False,
        type=int,
        default=7,
        dest="n_networks",
        choices=[7, 17],
    )
    optional.add_argument(
        "-p",
        "--parcels",
        help="Number of parcels to use.",
        required=False,
        type=int,
        default=100,
        dest="n_parcels",
        choices=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    )
    optional.add_argument(
        "--method",
        help="Method to decode the ROI image.",
        required=False,
        type=str,
        default="association",
        dest="method",
        choices=["association", "chi", "brainmap"],
    )
    optional.add_argument("-v", "--version", action="version", version=("%(prog)s " + __version__))

    parser._action_groups.append(optional)

    return parser


def wheres_waldo(rois, output, out_dir=".", n_networks=7, n_parcels=100, method="association"):
    # Download the Schaefer2018_100Parcels_7Networks_order_FSLMNI152_1mm.Centroid_RAS.csv file
    # from gh_url and save it to the current directory.
    gh_url = (
        "https://raw.githubusercontent.com/ThomasYeoLab/CBIG/master/stable_projects/"
        "brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/MNI/"
        "Centroid_coordinates"
    )

    print(
        f"Downloading Schaefer 2018 parcellation with {n_parcels} parcels and {n_networks}"
        f"networks..."
    )
    csv_file = (
        f"{gh_url}/Schaefer2018_{n_parcels}Parcels_{n_networks}Networks_order_FSLMNI152_1mm"
        f".Centroid_RAS.csv"
    )
    schaefer_info = pd.read_csv(csv_file, error_bad_lines=False)

    # Load Schaefer atlas from nilearn
    print("Loading Schaefer atlas...")
    schaefer_atlas = fetch_atlas_schaefer_2018(n_rois=n_parcels, yeo_networks=n_networks)
    atlas_img = nib.load(schaefer_atlas.maps)

    # Initialize empty directory to store the results
    dict_keys = ["values", "roi_label", "FS_coords", "MNI_152_coords", "location_detail"]
    output_dict = {key: [] for key in dict_keys}

    # Loop through each ROI and get details
    for roi in rois:
        print(f"Gettin details for {roi} ROI...")

        # Name of the ROI
        output_dict["values"].append(
            schaefer_info["ROI Name"][roi].rsplit(f"{n_networks}Networks_", 1)[1]
        )

        # ROI label
        output_dict["roi_label"].append(schaefer_info["ROI Name"][roi])

        # FS coordinates
        fs_coordinates = [
            schaefer_info["R"][roi],
            schaefer_info["A"][roi],
            schaefer_info["S"][roi],
            1,
        ]
        output_dict["FS_coords"].append(fs_coordinates)

        # MNI 152 coordinates
        output_dict["MNI_152_coords"].append(get_MNI_152(fs_coordinates))

        # Location detail
        output_dict["location_detail"].append(location_details(roi, atlas_img, method))

    # Save the results to a csv file
    print(f"Saving results to {output}...")
    output_df = pd.DataFrame(output_dict)
    output_df.to_csv(output, index=False)


def _main(argv=None):
    options = _get_parser().parse_args(argv)
    wheres_waldo(**vars(options))


if __name__ == "__main__":
    _main(sys.argv[1:])
