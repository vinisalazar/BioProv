__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Testing for the programs package.
"""

from bioprov.programs import prodigal, prokka, kaiju, kaiju2table
from bioprov.data import synechococcus_genome
from bioprov import Sample


def test_prodigal():
    """
    Testing the 'prodigal' program.
    :return:
    """
    s = Sample("Synechococcus", files={"assembly": synechococcus_genome})
    p = prodigal()
    p.create_func(s, preffix_tag="assembly")
    p.run()
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


def test_kaiju2table():
    """
    Testing the 'kaiju2table' program
    :return:
    """
    s = Sample("Synechococcus", files={"kaiju_output": synechococcus_genome})
    _ = kaiju2table(s)
