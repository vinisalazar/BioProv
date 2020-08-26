__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Testing for the Sample module.
"""
from os import remove, path
from bioprov import Sample, Project, SequenceFile, read_csv, from_json
from bioprov.src.sample import dict_to_sample, json_to_dict
from bioprov.data import synechococcus_genome, picocyano_dataset

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


def test_Project():
    """
    Testing for the Project class.
    :return:
    """
    ss = Project()
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
    sampleset_ = read_csv(
        picocyano_dataset, index_col="sample-id", sequencefile_cols="assembly-file",
    )
    assert len(sampleset_) > 0


def test_json_Sample():
    """
    Testing for JSON methods for the Sample class.
    :return:
    """
    sample = create_sample(attributes)

    # Test json methods
    sample.to_json()
    assert sample.files[
        "json"
    ].exists, f"Did not create JSON output for Sample '{sample.name}'."

    # Import JSON
    d = json_to_dict(str(sample.files["json"]))
    j, j_ = dict_to_sample(d), from_json(str(sample.files["json"]))
    for (k1, v1), (k2, v2), (k3, v3) in zip(
        sample.__dict__.items(), j.__dict__.items(), j_.__dict__.items()
    ):
        if any(k == "files" for k in (k1, k2, k3)):
            pass
        else:
            assert k1 == k2 == k3
            assert v1 == v2 == v3, f"Values \n'{v1}'\n'{v2}'\n'{v3}'\n differ"
    remove(str(sample.files["json"]))


def test_json_SampleSet():
    """
    Testing for JSON methods in Project class.
    :return:
    """
    ss = read_csv(picocyano_dataset, sequencefile_cols="assembly-file",)
    ss.tag = "Synechococcus"
    ss.to_json()
    json_out = ss.tag + ".json"
    assert path.isfile(json_out), f"Did not create JSON output for Project '{ss.tag}'."
    ss = from_json(json_out)
    assert isinstance(ss, Project)
    remove(json_out)
