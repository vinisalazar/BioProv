__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.8"


"""
Testing for the Config module.
"""

from bioprov import Config
from os import environ


def test_Config():
    """
    Testing for the Config class
    :return:
    """
    config = Config()
    assert config.env.env_set == frozenset(environ.items())
    assert config.user == config.env.user
    assert config.genomes.exists()
    assert config.data.exists()
