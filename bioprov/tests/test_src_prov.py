__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Testing for prov module.
    - ProjectProv class
"""

from bioprov import read_csv
from bioprov.data import picocyano_dataset
from bioprov.src.prov import ProjectProv
from prov.dot import prov_to_dot

project = read_csv(
    picocyano_dataset, sequencefile_cols="assembly-file", tag="picocyanobacteria"
)


def test_ProjectProv():
    """
    Tests the construction of an instance of ProjectProv.
    :return:
    """
    prov_ = ProjectProv(project)
    provdoc = prov_.provdoc
    dot = prov_to_dot(provdoc)
