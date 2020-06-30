"""
Contains the Program class and related functions.

To-do:
    - implement ParameterDict
"""
import subprocess


class Program:
    """
    Class for holding information about programs.
    """

    def __init__(self, name, params=None, tag=None, path=None, cmd=None, version=None):
        """
        :param name: Name of the program being called.
        :param params: Dictionary of parameters.
        :param tag: Tag to call the program if different from name. Default: self.name
        :param path: A full path to the program's binary. Default: get from self.name.
        :param cmd: A command string to call the program. Default: build from self.path and self.params.
        :param version: Version of the program.
        """
        self.name = name
        if isinstance(params, dict):
            params_ = dict()
            for k, v in params.items():
                if isinstance(v, Parameter):
                    v.program, v.tag = self
                    params_[k] = v
                else:
                    params_[k] = Parameter(k, v, program=self)
            params = params_
        elif isinstance(params, Parameter):
            params.program = self
            params = {params.key: params}
        elif params is None:
            params = dict()
        self.params = params
        self.param_str = generate_param_str(self.params)
        self.tag = tag
        self.path = path
        self.cmd = cmd
        self.version = version
        if tag is None:
            self.tag = self.name
        if path is None:
            self.path = subprocess.getoutput(f"which {self.name}")
        if cmd is None:
            self.cmd = self.generate_cmd()

    def __repr__(self):
        return f"Program '{self.name}' with {len(self.params)} parameter(s)."

    def generate_cmd(self):
        """
        Generates command string to execute.
        :return: command string
        """
        return " ".join([self.path, self.param_str]).strip()

    def add_parameter(self, parameter, _print=True):
        """
        Adds a parameter to the current instance and updates the command.

        :param parameter: an instance of the Parameter class.
        :param _print: whether to print the parameter has been added.
        :return:
        """
        k, v = parameter.key, parameter.value
        parameter.program = self
        self.params[k] = parameter
        self.param_str = generate_param_str(self.params)
        self.cmd = self.generate_cmd()
        if _print:
            print(f"Added parameter {k} with value '{v}' to program {self.name}")

    def run(self):
        pass

    pass


class Parameter:
    """
    Class holding information for parameters.
    """

    def __init__(
        self,
        key=None,
        value=None,
        tag=None,
        program=None,
        cmd_string=None,
        description=None,
        kind=None,
    ):
        """
        :param key: Key of the parameter, e.g. '-h' for help command.
        :param value: Value of the parameter.
        :param tag: A tag of the parameter.
        :param program: The program to which the parameter belongs to. Must be an instance of the Program class.
        :param cmd_string: String representation of the parameter in a command.
        :param description: description of the parameter.
        :param kind: Kind of parameter. May be 'input', 'output', 'misc', or None.
        """
        self.key = key
        self.program = program
        self.value = value
        self.tag = tag
        self.cmd_string = cmd_string
        self.description = description
        self.kind = kind
        self.dict = {key: value}

        assert kind in {
            "input",
            "output",
            "misc",
            None,
        }, "Be sure that 'kind' is one of {'input', 'output', 'misc', None},"

        if tag is None:
            self.tag = self.key
        if cmd_string is None:
            self.cmd_string = key + " " + str(value)

    def __repr__(self):
        if self.value == "":
            str_ = f"Parameter {self.key} with no value."
        else:
            str_ = f"Parameter {self.key} with value {self.value}."
        if self.description is not None:
            str_ += " Description: " + f"'{self.description}.'"
        if self.kind is not None:
            str_ += " Kind: " + f"'{self.kind}."
        return str_

    pass


# Replace 'params' here with ParameterDict
def generate_param_str(params):
    """
    To-do: improve this docstring
    Generates a string from a dictionary of parameters
    :param params: Dictionary of parameters.
    :return:
    """
    str_ = ""
    if not params:
        return str_
    elif params:
        for k, v in params.items():
            # If is a Parameter class instance, we inherit the corresponding tags.
            if isinstance(v, Parameter):
                str_ += v.cmd_string + " "
            else:
                str_ += (
                    k + " " + v + " "
                )  # Else we construct the string from the the provided dict.
        param_str = str_.strip()
    else:
        # To-do: add more parameters options. List of tuples, List of Parameter instances, etc.
        print("Must provide either a string or a dictionary for the parameters!")
        raise TypeError
    return param_str