__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


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
    p_ = prodigal(s)
    p_.run()
    pass


def test_prokka():
    """
    Testing the 'prokka' program.
    :return:
    """
    s = Sample("Synechococcus", files={"assembly": synechococcus_genome})
    prokka_program = prokka(s)
    prokka_params = list(prokka_program.serializer()["params"].keys())

    expected_params = ["--prefix", "--outdir", "--cpus", ""]

    assert prokka_params == expected_params


def test_kaiju():
    """
    Testing the 'kaiju' program.
    :return:
    """
    s = Sample("Synechococcus", files={"R1": synechococcus_genome, "R2": "r2.fastq"})
    kaiju_program = kaiju(s)
    kaiju_params = list(kaiju_program.serializer()["params"].keys())

    expected_params = ["-t", "-i", "-j", "-f", "-z", "-o"]

    assert kaiju_params == expected_params


def test_kaiju2table():
    """
    Testing the 'kaiju2table' program
    :return:
    """
    s = Sample("Synechococcus", files={"kaiju_output": synechococcus_genome})
    kaiju2tab_program = kaiju2table(s)
    kaiju2tab_params = list(kaiju2tab_program.serializer()["params"].keys())

    expected_params = ["-o", "-t", "-n", "-r"]

    assert kaiju2tab_params == expected_params
