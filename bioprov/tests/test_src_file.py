__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Testing for the File module.
"""
import bioprov as bp
from bioprov import File, SeqFile, utils
from bioprov.src.files import seqrecordgenerator
from coolname import generate_slug
from pathlib import Path
from bioprov.data import synechococcus_genome
from prov.model import ProvEntity


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
        "no_size": nf.size == 0,
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

    # test hashes
    nf.exists = True
    nf.replace_path("", "", warnings=True)  # no cover
    nf.sha1 = generate_slug(2)
    # nf.replace_path(non_existing, bp.__file__)  # no cover
    _ = f.entity
    f.entity = ProvEntity(None, generate_slug(2))


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

    # Testing generator property
    genome.generator = None
    _ = genome.generator

    # Testing seqstats property
    genome.seqstats = None
    _ = genome.seqstats

    # Test _calculate_seqstats args
    genome._calculate_seqstats(percentage=True, megabases=True)
    genome._calculate_seqstats(calculate_gc=False)

    # Test FileNotFound warning
    none = seqrecordgenerator(nf_genome.path, "fasta", warnings=True)
    assert none is None, f"{none} should be a NoneType object!"
