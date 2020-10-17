__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.8"


"""
Testing for prov module.
    - BioProvDocument class
"""

from os import environ
from bioprov import read_csv
from bioprov.data import picocyano_dataset
from bioprov.src.prov import BioProvDocument
from bioprov.src.config import EnvProv

project = read_csv(
    picocyano_dataset, sequencefile_cols="assembly", tag="picocyanobacteria"
)


def test_EnvProv():
    """
    Tests the construction of an instance of EnvProv.
    :return:
    """
    env = EnvProv()
    for statement in (
        env.env_set == frozenset(environ.items()),
        env.env_hash == hash(env.env_set),
    ):
        assert statement


def test_BioProvDocument():
    """
    Tests the construction of an instance of BioProvDocument.
    :return:
    """
    _ = BioProvDocument(project)
