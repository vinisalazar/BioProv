__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


"""
Testing for the programs package.
"""

from bioprov import Sample
from bioprov.data import synechococcus_genome
from bioprov.programs import (
    blastn,
    blastp,
    muscle,
    mafft,
    diamond,
    kallisto_quant,
    kaiju,
    kaiju2table,
    prodigal,
    prokka,
)


def test_diamond():

    s = Sample("Synechococcus", files={"query": synechococcus_genome})
    reference_db = "./path_to_a_valid_blastdb"

    dmnd_extra = diamond(
        blast_type="blastp",
        sample=s,
        db=reference_db,
        extra_flags=["--sensitive", "--log"],
    )

    expected = [
        "blastp",
        "--db",
        "--outfmt",
        "--query",
        "--out",
        "--sensitive",
        "--log",
    ]

    dmnd_params = list(dmnd_extra.serializer()["params"].keys())

    assert dmnd_params == expected


def test_blastn():

    s = Sample("Synechococcus", files={"query": synechococcus_genome})
    reference_db = "./path_to_a_valid_blastdb"

    blast = blastn(s, reference_db)
    blast_params = blast.serializer()["params"]

    expected = ["-db", "-outfmt", "-query", "-out"]

    assert list(blast_params.keys()) == expected
    assert blast_params["-outfmt"]["value"] == "6"


def test_blastp():

    s = Sample("Synechococcus", files={"query": synechococcus_genome})
    reference_db = "./path_to_a_valid_blastdb"

    blast = blastp(s, reference_db)
    blast_params = blast.serializer()["params"]

    expected = ["-db", "-outfmt", "-query", "-out"]

    assert list(blast_params.keys()) == expected
    assert blast_params["-outfmt"]["value"] == "6"


def test_muscle():

    s = Sample("Synechococcus", files={"input": synechococcus_genome})

    muscle_prog = muscle(sample=s, msf=True)
    muscle_params = muscle_prog.serializer()["params"]

    expected = ["-in", "-out", "-msf"]

    assert list(muscle_params.keys()) == expected


def test_mafft():

    s = Sample("Synechococcus", files={"input": synechococcus_genome})

    mafft_prog = mafft(s)
    mafft_params = mafft_prog.serializer()["params"]

    expected = ["", ">"]

    assert list(mafft_params.keys()) == expected


def test_kallisto():

    s = Sample(
        "Synechococcus", files={"R1": "fake_first_read", "R2": "fake_second_read"}
    )

    kall_prog = kallisto_quant(s, "fake_index_file.idx")
    kall_params = list(kall_prog.serializer()["params"].keys())

    expected = ["quant", "--index", "--output-dir"]

    assert kall_params[0:3] == expected
    assert len(kall_params) == 5


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
