__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


"""
Testing for prov module.
    - BioProvDocument class
"""

from os import environ

from pydot import Dot

from bioprov import read_csv
from bioprov.data import picocyano_dataset
from bioprov.src.config import Environment
from bioprov.src.prov import BioProvDocument
from bioprov.utils import dict_to_sha1

project = read_csv(
    picocyano_dataset, sequencefile_cols="assembly", tag="picocyanobacteria"
)


def test_EnvProv():
    """
    Tests the construction of an instance of Environment.
    :return:
    """
    env = Environment()
    for statement in (
        env.env_dict == dict(environ.items()),
        env.env_hash == dict_to_sha1(env.env_dict),
    ):
        assert statement


def test_BioProvDocument():
    """
    Tests the construction of an instance of BioProvDocument.
    :return:
    """
    # The BioProvDocument constructor with add_attributes=True
    # is tested in the test_src_main.py module
    prov = BioProvDocument(project)

    # __repr__
    assert str(prov).startswith("BioProvDocument")

    # dot property
    assert type(prov.dot) == Dot
    prov.dot = Dot()
