__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Testing for Program module
    - Program class
    - Parameter class
    - Run class
"""

from bioprov.src.program import (
    generate_param_str,
    Parameter,
    parse_params,
    Program,
    Run,
)
from bioprov.utils import random_string


def test_Program():
    """
    Testing for the Program class.
    :return:
    """
    attributes = {
        "name": "prodigal",
        "params": {"-h": ""},
        "tag": "gene annotation",
        "found": True,
        "version": "Prodigal V2.6.3: February, 2016",
    }
    p = Program(name="prodigal")
    for attr, v in attributes.items():
        if (
            attr != "version"
        ):  # check if it gets the version automatically (won't see version attribute).
            setattr(p, attr, v)
            assert getattr(p, attr) == v, f"{attr} attribute is wrong!"
    assert p.cmd == p.generate_cmd()
    r32 = random_string(32)
    some_random_program = Program(r32)
    assert (
        not some_random_program.found
    ), "You shouldn't a program called {} lying around!".format(r32)


def test_Parameter():
    """
    Testing for the Parameter class.
    :return:
    """
    attributes = {
        "key": "-h",
        "value": "",
        "tag": "help",
        "description": "Show help message.",
        "kind": "misc",
    }
    param = Parameter()
    for attr, v in attributes.items():
        setattr(param, attr, v)
        assert getattr(param, attr) == v, f"{attr} attribute is wrong!"
    assert isinstance(param.dict, dict), "Parameter dictionary not building correctly."


def test_Run():
    """
    Testing for the Run class.
    :return:
    """
    attributes = {"program": Program("prodigal", {"-h": ""})}
    run_ = Run()
    for attr, v in attributes.items():
        setattr(run_, attr, v)

    # Check the status and run
    assert run_.status is "Pending"
    run_.run()

    # Check status again
    assert (
        run_.start_time == run_.end_time
    ), "This test may fail occasionally. Run it again."  # This should be the same for the '-h' parameter.
    assert run_.finished is True
    assert run_.status is "Finished"


def test_parse_params():
    """
    Testing for the parse_params() function.
    :return:
    """
    params = {
        "-i": "some_file.fna",
        "-a": Parameter("-a", "some_other_file.faa", "some other file"),
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
