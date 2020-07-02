"""
Testing for the Config module.
"""

from bioprov.Config import Config


def test_Config():
    """
    Testing for the Config class
    :return:
    """
    config = Config()
    assert config.genomes_dir.exists()
    assert config.data_dir.exists()
