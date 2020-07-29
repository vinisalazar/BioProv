__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Testing for the SequenceFile module.

To-do:
    - add test for seqstats function
    - add test for seqrecordgenerator function
"""
from bioprov import SequenceFile
from bioprov.src.sequencefile import seqstats
from bioprov.utils import random_string
from bioprov.data import synechococcus_genome


def test_seqstats():
    """
    Testing for seqstats function.
    :return:
    """
    genome = SequenceFile(synechococcus_genome)
    seqstats_ = seqstats(str(genome))
    bps, gc = 2696255, 0.55484
    attributes = {
        "number_seqs": 1,
        "total_bps": bps,
        "gc": gc,
        "avg_bp": bps,
        "median_bp": bps,
        "n50": bps,
        "min_bp": bps,
        "max_bp": bps,
    }
    for attr, statement in attributes.items():
        assert getattr(seqstats_, attr) == statement
    assert len(genome) == bps  # Test __len__() method.
    pass


def test_SequenceFile():
    """
    Tests objects in the SequenceFile module:
        - existing SequenceFile instance
        - seqrecord_generator()
    :return:
    """
    tag = "Synechococcus elongatus PCC 6301"
    genome = SequenceFile(synechococcus_genome, tag, import_data=True)
    nf_genome, nf_tag = random_string(), random_string(4)
    nf_genome = SequenceFile(nf_genome, nf_tag)

    # Instance where file exists
    existing_instance = {
        "exists": genome.exists,
        "tag": genome.tag == tag,
        "class": type(genome) == SequenceFile,
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
        "class": type(nf_genome) == SequenceFile,
        "records": nf_genome.records
        is None,  # To-do: implement more exceptions to __getitem__
    }
    for dict_ in (existing_instance, non_existing_instance):
        for k, statement in dict_.items():
            assert statement, f"{k} did not pass!"

    pass
