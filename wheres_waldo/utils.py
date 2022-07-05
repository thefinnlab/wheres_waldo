import numpy as np
import pandas as pd


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


def schaeffer_region_info(list_of_reg):
    data_dir = "/dartfs/rc/lab/F/FinnLab/clara/K99_EventSeg/data/"
    s_dictionary = pd.read_csv(
        data_dir
        + "/_masks/"
        + "Schaefer2018_100Parcels_7Networks_order_FSLMNI152_1mm.Centroid_RAS.csv"
    )

    values = []
    roi_label = []
    FS_coords = []
    MNI_152_coords = []
    loc_det = []
    for x in list_of_reg:
        values.append(s_dictionary["ROI Name"][x].rsplit("7Networks_", 1)[1])
        roi_label.append(s_dictionary["ROI Label"][x])
        temp = []
        temp.append(s_dictionary["R"][x])
        temp.append(s_dictionary["A"][x])
        temp.append(s_dictionary["S"][x])
        temp.append(1)
        FS_coords.append(temp)
        MNI_152_coords.append(get_MNI_152(temp))
        loc_det.append(location_details(x))

    comb = {
        "node_list": list_of_reg,
        "parc_node": roi_label,
        "region": values,
        "FS_coords": FS_coords,
        "MNI_152_coords": MNI_152_coords,
        "location_detail": loc_det,
    }
    comb = pd.DataFrame(comb)

    return comb

def location_details(x):
    # TODO: write function to get location details with NiMARE
    print(x)
