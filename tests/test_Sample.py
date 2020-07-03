"""
Testing for the Sample module.
"""
from os import remove
from bioprov.SequenceFile import SequenceFile
from bioprov.Sample import Sample, SampleSet, read_csv, dict_to_sample, json_to_dict
from bioprov.data import synechococcus_genome, synechococcus_dataset

# Sample attributes for testing
attributes = {
    "name": "GCF_000010065.1_ASM1006v1",
    "tag": "Synechococcus elongatus PCC 6301",
    "files": {"assembly": SequenceFile(synechococcus_genome, "assembly")},
    "attributes": {"habitat": "freshwater"},
}


def create_sample(attributes_):
    sample = Sample()
    for attr, v in attributes_.items():
        setattr(sample, attr, v)

    return sample


def test_Sample():
    """
    Testing for the Sample class.
    :return:
    """
    sample = create_sample(attributes)
    for attr, v in attributes.items():
        assert getattr(sample, attr) == v

    protein_path = str(synechococcus_genome).replace("fna", "faa")
    sample.add_files({"proteins": protein_path})
    assert sample.files[
        "assembly"
    ].exists, f"Couldn't find file in path {synechococcus_genome}. Check bioprov's data directory."


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
    sampleset_ = read_csv(synechococcus_dataset, sequencefile_cols="assembly-file")
    assert len(sampleset_) > 0


def test_json():
    """
    Testing for JSON methods in the Sample module.
    :return:
    """
    sample = create_sample(attributes)

    # Test json methods
    sample.to_json()
    assert sample.files["json"].exists

    # Import JSON
    d = json_to_dict(str(sample.files["json"]))
    j = dict_to_sample(d)
    for (k1, v1), (k2, v2) in zip(sample.__dict__.items(), j.__dict__.items()):
        if k1 or k2 == "files":
            pass
        else:
            assert k1 == k2
            assert v1 == v2, f"Values \n'{v1}'\n and '\n{v2}\n' differ"
    remove(str(sample.files["json"]))


ss = read_csv(synechococcus_dataset, sequencefile_cols="assembly-file")
