"""
Testing for the Sample module.
"""
from bioprov.Sample import Sample, SampleSet, read_csv
from bioprov.data import synechococcus_genome, synechococcus_dataset

# Sample attributes for testing
attributes = {
    "name": "GCF_000010065.1_ASM1006v1",
    "tag": "Synechococcus elongatus PCC 6301",
    "files": dict(),
    "attributes": {"habitat": "freshwater"},
}


def test_Sample():
    """
    Testing for the Sample class.
    :return:
    """
    sample = Sample()
    for attr, v in attributes.items():
        setattr(sample, attr, v)
        assert getattr(sample, attr) == v

    assembly_path = synechococcus_genome
    protein_path = str(synechococcus_genome).replace("fna", "faa")
    sample.add_files({"assembly": assembly_path})
    sample.add_files({"proteins": protein_path})
    assert sample.files[
        "assembly"
    ].exists, f"Couldn't find file in path {assembly_path}."


def test_SampleSet():
    """
    Testing for the SampleSet class.
    :return:
    """
    ss = SampleSet()
    sample = Sample()
    for attr, v in attributes.items():
        setattr(sample, attr, v)

    ss[sample.name] = sample
    assert len(ss) == 1


def test_from_df():
    """
    Testing for the from and read_csv functions.
    :return:
    """
    ss = read_csv(synechococcus_dataset, sequencefile_cols="assembly-file")
    assert len(ss) > 0


ss = read_csv(synechococcus_dataset, sequencefile_cols="assembly-file")
