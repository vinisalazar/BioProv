"""
Testing for Program module
    - Program class
    - Parameter class
    - Run class
"""

from bioprov.Program import Program, Run, Parameter, parse_params, generate_param_str


def test_Program():
    """
    Testing for the Program class.
    :return:
    """
    attributes = {
        "name": "prodigal",
        "params": {"-h": ""},
        "tag": "gene annotation",
        "version": "v2.6.2",
    }
    p = Program()
    for attr, v in attributes.items():
        setattr(p, attr, v)
        if attr != "params":
            assert getattr(p, attr) == v, f"{attr} attribute is wrong!"
        else:
            assert all(isinstance(v_, Parameter) for k, v_ in getattr(p, attr).items())
    assert p.cmd == p.generate_cmd()


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
    run = Run()
    for attr, v in attributes.items():
        setattr(run, attr, v)

    # Check the status and run
    assert run.status is "Pending"
    run.run()

    # Check status again
    assert run.finished is True
    assert run.status is "Finished"


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
