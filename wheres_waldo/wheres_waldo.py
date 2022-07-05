import sys
import argparse
from wheres_waldo import __version__

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
        type=str,
        nargs="+",
        dest="rois",
    )
    optional.add_argument("-v", "--version", action="version", version=("%(prog)s " + __version__))

    parser._action_groups.append(optional)

    return parser


def wheres_waldo(rois):
    # TODO: write main function
    print(rois)


def _main(argv=None):
    options = _get_parser().parse_args(argv)
    wheres_waldo(**vars(options))


if __name__ == "__main__":
    _main(sys.argv[1:])
