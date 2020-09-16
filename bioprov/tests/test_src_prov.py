__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.2"


"""
Testing for prov module.
    - BioProvProject class
"""

from os import environ
from bioprov import read_csv
from bioprov.data import picocyano_dataset
from bioprov.src.prov import EnvProv, BioProvDocument, BioProvProject

project = read_csv(
    picocyano_dataset, sequencefile_cols="assembly-file", tag="picocyanobacteria"
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
    _ = BioProvDocument()


def test_BioProvProject():
    """
    Tests the construction of an instance of BioProvProject.
    :return:
    """
    _ = BioProvProject(project)
