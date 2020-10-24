__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Testing for the bioprov.src.main module.
 Tests the following classes:
    - Program
    - Parameter
    - Run
    - Sample
    - Project
    
 Also tests JSON and tab-delimited serializer methods.
"""

# To-do: organize this
import datetime
import pandas as pd
from bioprov.src.main import (
    generate_param_str,
    Parameter,
    parse_params,
    Program,
    Run,
)
from coolname import generate_slug
from os import remove
from bioprov import (
    Sample,
    Project,
    SeqFile,
    read_csv,
    write_json,
    from_json,
    BioProvDocument,
)
from bioprov.src.main import dict_to_sample, json_to_dict
from bioprov.data import synechococcus_genome, picocyano_dataset
from bioprov.programs import prodigal


def test_Program():
    """
    Testing for the Program class.
    :return:
    """
    _attributes = {
        "name": "prodigal",
        "params": {"-h": ""},
        "tag": "gene annotation",
        "found": True,
        "version": "Prodigal V2.6.3: February, 2016",
    }
    p = Program(name="prodigal")
    for attr, v in _attributes.items():
        if (
            attr != "version"
        ):  # check if it gets the version automatically (won't see version attribute).
            setattr(p, attr, v)
            assert getattr(p, attr) == v, f"{attr} attribute is wrong!"
    assert p.cmd == p.generate_cmd()
    slug = generate_slug(3)
    some_random_program = Program(slug)
    assert (
        not some_random_program.found
    ), f"You shouldn't have a program called {slug} lying around!"


def test_Parameter():
    """
    Testing for the Parameter class.
    :return:
    """
    _attributes = {
        "key": "-h",
        "value": "",
        "tag": "help",
        "description": "Show help message.",
        "kind": "misc",
    }
    param = Parameter()
    for attr, v in _attributes.items():
        setattr(param, attr, v)
        assert getattr(param, attr) == v, f"{attr} attribute is wrong!"
    assert isinstance(param.dict, dict), "Parameter dictionary not building correctly."


def test_Run():
    """
    Testing for the Run class.
    :return:
    """
    _attributes = {"program": Program("prodigal", {"-h": ""})}
    run_ = Run(_attributes["program"])

    # Check the status and run
    assert run_.status is "Pending"
    run_.run()

    # Check status again
    start_time, end_time = (
        datetime.datetime.strptime(time_, "%a %b %d %H:%M:%S %Y")
        for time_ in (run_.start_time, run_.end_time)
    )
    timedelta_secs = (start_time - end_time).total_seconds()
    duration_secs = datetime.datetime.strptime(run_.duration, "%H:%M:%S.%f").second
    assert (
        timedelta_secs < 5 and duration_secs < 5
    ), "This shouldn't take this long to run."
    assert run_.finished is True
    assert run_.status is "Finished"


def test_parse_params():
    """
    Testing for the parse_params() function.
    :return:
    """
    params = {
        "-i": "some_file.fna",
        "-a": Parameter(key="-a", value="some_other_file.faa", tag="some other file"),
    }
    dict_ = parse_params(params)
    assert isinstance(dict_, dict), "Parameter dictionary did not build correctly."


def test_generate_param_str():
    """
    Testing for generate_param_str() function.
    :return:
    """
    params = {
        "-i": "some_file.fna",
        "-a": Parameter("-a", "some_other_file.faa", "some other file"),
    }
    correct_string = "-i some_file.fna -a some_other_file.faa"
    test_string = generate_param_str(params)
    assert (
        test_string == correct_string
    ), f"Test string is\n'{test_string}'\nCorrect string is \n'{correct_string}'. "


"""
Testing for the Sample module.
"""

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
    assert type(sample.to_series()) == pd.Series


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
    assert type(ss.to_df()) == pd.DataFrame
    assert len(ss) == 1


def test_from_df():
    """
    Testing for the from and read_csv functions.
    :return:
    """
    sampleset_ = read_csv(
        picocyano_dataset,
        index_col="sample-id",
        sequencefile_cols="assembly",
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


def test_project_json_and_prov(debug=False):
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

    def create_prov(_project):
        return BioProvDocument(_project, add_attributes=True)

    def export_prov_json(_path, _projectprov):
        json = _projectprov.ProvDocument.serialize()
        write_json(json, _path=_path)

    project = import_project()
    add_and_run_programs(project)

    # Test export
    json_out = "./gentax_picocyano.json"
    export_json(json_out, project)

    from_json(json_out)
    project = from_json(json_out, replace_path=("", ""))
    json_out_2 = "./gentax_picocyano_copy.json"
    export_json(json_out_2, project)

    prov = create_prov(project)
    prov_json_out = "./gentax_picocyano_prov.json"
    export_prov_json(prov_json_out, prov)

    # Clean up
    for f in (json_out, json_out_2, prov_json_out):
        remove(f)

    # Useful for debugging
    if debug:
        return project, prov
