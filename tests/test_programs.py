"""
Testing for the programs package.
"""

from bioprov.programs import prodigal, prokka, kaiju
from bioprov.data import synechococcus_genome
from bioprov import Sample


def test_prodigal():
    """
    Testing the 'prodigal' program.
    :return:
    """
    s = Sample("Synechococcus", files={"assembly": synechococcus_genome})
    _ = prodigal(s)
    pass


def test_prokka():
    """
    Testing the 'prokka' program.
    :return:
    """
    s = Sample("Synechococcus", files={"assembly": synechococcus_genome})
    _ = prokka(s)
    pass


def test_kaiju():
    """
    Testing the 'kaiju' program.
    :return:
    """
    s = Sample("Synechococcus", files={"R1": synechococcus_genome, "R2": ""})
    _ = kaiju(s)
