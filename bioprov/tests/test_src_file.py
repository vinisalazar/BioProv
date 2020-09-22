__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.2"


"""
Testing for the File module.
"""
import bioprov as bp
from bioprov import File, SeqFile, utils
from coolname import generate_slug
from pathlib import Path
from bioprov.data import synechococcus_genome


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
    f = File(file, tag)
    non_existing = generate_slug(2)
    nf = File("./" + non_existing)
    attributes = {
        # File class - existing file
        "path": f.path == Path(file).absolute(),
        "name": f.name == f.path.stem,
        "dir": f.directory == f.path.parent,
        "extension": f.extension == f.path.suffix,
        "tag": f.tag == tag,
        "exists": f.exists is True,
        "repr": f.__repr__() == str(f.path),
        # Non existing file
        "non_existing": nf.exists is False,
        "no_size": nf.size is 0,
        "nf_repr": nf.__repr__() == str(nf.path),
        # get_size() function
        "get_size": f.size == utils.get_size(f.path),
        "raw_get_size": f.raw_size
        == utils.get_size(f.path, convert=False),  # get_size(convert=False)
        # Convert bytes function
        "convert_bytes": utils.convert_bytes(2 ** 10) == "1.0 KB",
    }
    for k, statement in attributes.items():
        assert statement, f"{k} did not pass!"


def test_SeqFile():
    """
    Tests the SeqFile constructor.
    :return:
    """
    tag = "Synechococcus elongatus PCC 6301"
    genome = SeqFile(synechococcus_genome, tag, import_records=True)
    nf_genome, nf_tag = generate_slug(2), generate_slug(2)
    nf_genome = SeqFile(nf_genome, nf_tag)

    # Instance where file exists
    existing_instance = {
        "exists": genome.exists,
        "tag": genome.tag == tag,
        "class": type(genome) == SeqFile,
        "records": all(
            (
                type(genome.records) == dict,
                len(genome.records),
                genome.records["NC_006576.1"],
            )
        ),
    }

    for dict_ in (existing_instance,):
        for k, statement in dict_.items():
            assert statement, f"{k} did not pass!"
