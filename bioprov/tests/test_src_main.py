__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


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

# TODO: organize this
import datetime
from os import remove
from pathlib import Path

import pandas as pd
from coolname import generate_slug

from bioprov import (
    Sample,
    Project,
    SeqFile,
    read_csv,
    write_json,
    from_json,
    BioProvDocument,
    BioProvDB,
)
from bioprov.data import synechococcus_genome, picocyano_dataset
from bioprov.programs import prodigal
from bioprov.src.main import (
    generate_param_str,
    Parameter,
    File,
    Directory,
    parse_params,
    Program,
    PresetProgram,
    Run,
    dict_to_sample,
    json_to_dict,
)
from bioprov.utils import dict_to_sha1, Warnings


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
    assert str(run_).startswith("Run")


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
    # test Parameter.__repr__ method
    assert str(dict_["-a"]).startswith(
        "Parameter"
    ), "Parameter.__repr__() method failed"
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


def test_preset_extra_flags():

    grep_test = PresetProgram(name="grep", extra_flags=["--version", "--help"])

    assert "--version --help" in grep_test.cmd


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

    # test Directory getter and setter
    assert sample.directory.path == sample.files["proteins"].directory
    sample.directory = Path(".")
    assert sample.directory.path == Path(".").absolute()

    # test Sample.__delitem__
    del sample["proteins"]


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
    project_ = read_csv(
        picocyano_dataset,
        index_col="sample-id",
        sequencefile_cols="assembly",
    )
    assert len(project_) > 0


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


# TODO: improve this hideous test.
def test_project_json_and_prov():
    def import_project():
        _project = read_csv(
            picocyano_dataset,
            sequencefile_cols="assembly",
            tag="gentax_picocyano",
            import_data=True,
        )

        # Remove samples to make testing faster.
        for n in range(3):
            _project.samples.popitem()

        return _project

    def add_and_run_programs(_project, _out):
        for k, _sample in _project.items():
            _sample.add_programs(prodigal(sample=_sample))
            _sample.run_programs()
        _out = File(_out)
        _project.add_files(_out)
        ls = Program("ls", params={">": str(_project.files["ls_out"])})
        _project.add_programs(ls)
        _project.programs["ls"].run()

    def export_json(path, _project):
        return _project.to_json(path)

    def create_prov(_project):
        return BioProvDocument(_project, add_attributes=True)

    def export_prov_json(_path, _projectprov):
        json = _projectprov.ProvDocument.serialize()
        write_json(json, _path=_path)

    project = import_project()
    out = "./ls_out.txt"
    add_and_run_programs(project, out)

    # Test export
    json_out = "./gentax_picocyano.json"
    export_json(json_out, project)

    project = from_json(json_out, replace_path=("", ""))
    csv = f"{project.tag}.csv"
    project.to_csv(csv)
    json_out_2 = "./gentax_picocyano_copy.json"
    export_json(json_out_2, project)
    pwd = Directory(".", "pwd")
    pwd.add_files_to_object(project)
    pwd.add_files_to_object(project, kind="ds")

    prov = create_prov(project)
    prov_json_out = "./gentax_picocyano_prov.json"
    export_prov_json(prov_json_out, prov)
    provn_path = prov_json_out.replace("prov.json", "provn.txt")
    prov.write_provn(provn_path)

    # Clean up - JSON, PROVN, csv
    for f in (out, json_out, json_out_2, prov_json_out, provn_path, csv):
        assert Path(f).exists(), Warnings()["not_found"](f)
        remove(f)

    # Clean up - prodigal output
    for _, sample in project.items():
        for key, file in sample.files.items():
            if key != "assembly":  # we are keeping those
                remove(file.path)

    # Test DB, project.__delitem__, project.sha1
    project.db = BioProvDB(json_out_2)  # Let's not waste this variable
    project.update_db()

    # Maybe put this function in config
    def get_db_hash():
        result, query = project.query_db()
        _db_hash = dict_to_sha1(result)
        return _db_hash

    old_db_sha1 = get_db_hash()

    project.auto_update = True
    old_project_sha1 = project.sha1
    del project["GCF_000010065.1"]
    new_project_sha1 = project.sha1
    new_db_sha1 = get_db_hash()
    assert (
        new_project_sha1 != old_project_sha1
    ), "Project hashes aren't different, but Project has changed!"
    assert (
        old_db_sha1 != new_db_sha1
    ), "Database hashes aren't different, but Project.auto_update() is on and Project has changed!"

    # Clean up again
    remove(json_out_2)
