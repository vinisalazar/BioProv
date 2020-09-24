__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.3"


"""
Testing for the Sample module.
"""
from os import remove
from bioprov import (
    Sample,
    Project,
    SeqFile,
    read_csv,
    write_json,
    from_json,
    BioProvProject,
)
from bioprov.src.program import dict_to_sample, json_to_dict
from bioprov.data import synechococcus_genome, picocyano_dataset
from bioprov.programs import prodigal

# Sample attributes for testing
attributes = {
    "name": "GCF_000010065.1_ASM1006v1",
    "tag": "Synechococcus elongatus PCC 6301",
    "files": {"assembly": SeqFile(synechococcus_genome, "assembly")},
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
        picocyano_dataset, index_col="sample-id", sequencefile_cols="assembly",
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


def test_project_json_and_prov():
    def import_project():
        _project = read_csv(
            picocyano_dataset,
            sequencefile_cols="assembly",
            tag="gentax_picocyano",
            import_data=True,
        )

        return _project

    def add_and_run_programs(_project):
        for k, sample in _project.items():
            sample.add_programs(prodigal(sample=sample))
            sample.run_programs()

    def export_json(path, _project):
        return _project.to_json(path)

    def import_json(path):
        return from_json(path)

    def create_prov(_project):
        return BioProvProject(_project)

    def export_prov_json(_path, _projectprov):
        json = _projectprov.ProvDocument.serialize()
        write_json(json, _path=_path)

    project = import_project()
    add_and_run_programs(project)

    # Test export
    json_out = "./gentax_picocyano.json"
    export_json(json_out, project)

    # Test import
    project = import_json(json_out)
    json_out_2 = "./gentax_picocyano_copy.json"
    export_json(json_out_2, project)

    prov = create_prov(project)
    prov_json_out = "./gentax_picocyano_prov.json"
    export_prov_json(prov_json_out, prov)

    # breakpoint()

    # Clean up
    for f in (json_out, json_out_2, prov_json_out):
        remove(f)
