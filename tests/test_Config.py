__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Testing for the Config module.
"""

from bioprov import Config


def test_Config():
    """
    Testing for the Config class
    :return:
    """
    config = Config()
    assert config.genomes_dir.exists()
    assert config.data_dir.exists()
