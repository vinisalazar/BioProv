"""
Testing module for the package BioProv.

Tests include:
    - Imports;
    - Class generation and methods.
"""
import random
import string
from pathlib import Path

# Actual module
import bioprov as bp


def test_import_bioprov():
    """
    Test if the package can be imported correctly.
    :return: ImportError if not able to import.
    """
    try:
        import bioprov
    except ImportError:
        raise


def test_import_classes():
    """
    Test if all classes can be imported correctly.
    :return: ImportError if not able to import
    """
    try:
        from bioprov import Config, File, SequenceFile, get_size
    except ImportError:
        raise


def test_import_data():
    """
    Test if data can be imported correctly
    :return: ImportError if not able to import
    """
    try:
        from bioprov.data import data_dir, genomes_dir
    except ImportError:
        raise


def test_File():
    """
    Tests objects in the File module:
        - existing File instance
        - non-existing File instance
        - get_size(), convert_bytes()
    :return:
    """

    # Test existing file
    file, tag = bp.__file__, "Init file for BioProv."
    f = bp.File(file, tag)
    non_existing = randomString() + "." + randomString(3)
    nf = bp.File("./" + non_existing)
    attributes = {
        # File class - existing file
        "path": f.path == Path(file).absolute(),
        "name": f.name == f.path.stem,
        "dir": f.directory == f.path.parent,
        "extension": f.extension == f.path.suffix,
        "tag": f.tag == tag,
        "exists": f.exists is True,
        # Non existing file
        "non_existing": nf.exists is False,
        "no_size": nf.size is 0,
        "nf_repr": nf.__repr__()
        == f"Path {nf.name} in directory {nf.directory}. File does not exist.",
        # get_size() function
        "get_size": f.size == bp.get_size(f.path),
        "raw_get_size": f.raw_size
        == bp.get_size(f.path, convert=False),  # get_size(convert=False)
        "repr": f.__repr__()
        == f"File {f.name} with {f.size} in directory {f.directory}.",
        # Convert bytes function
        "convert_bytes": bp.convert_bytes(2 ** 10) == "1.0 KB",
    }
    for k, statement in attributes.items():
        assert statement, f"{k} did not pass!"


def test_SequenceFile():
    """
    Tests objects in the SequenceFile module:
        - existing SequenceFile instance
        - seqrecord_generator()
    :return:
    """
    genome_path = Path.joinpath(bp.genomes_dir, "GCF_000010065.1_ASM1006v1_genomic.fna")
    tag = "Synechococcus elongatus PCC 6301"
    genome = bp.SequenceFile(genome_path, tag)
    nf_genome, nf_tag = randomString(), randomString(4)
    nf_genome = bp.SequenceFile(nf_genome, nf_tag)

    # Instance where file exists
    existing_instance = {
        "exists": genome.exists,
        "tag": genome.tag == tag,
        "class": type(genome) == bp.SequenceFile,
        "records": all(
            (
                type(genome.records) == dict,
                len(genome.records),
                genome.records["NC_006576.1"],
            )
        ),
    }

    # Check instance where the file does not exist
    non_existing_instance = {
        "exists": nf_genome.exists is False,
        "tag": nf_genome.tag == nf_tag,
        "class": type(nf_genome) == bp.SequenceFile,
        "records": nf_genome.records
        is False,  # To-do: implement more exceptions to __getitem__
    }
    for dict_ in (existing_instance, non_existing_instance):
        for k, statement in dict_.items():
            assert statement, f"{k} did not pass!"

    pass


def randomString(n=8):
    """
    Generate random strings for testings
    :param n: Length of string.
    :return: Random string of n characters.
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(n))
