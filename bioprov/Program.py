"""
Contains the Program class and related functions.
"""
import subprocess
from pathlib import Path


class Program:
    """
    Class for holding information about programs.
    """

    def __init__(
        self, name, params=False, tag=False, path=False, cmd=False,
    ):
        """
        :param name: Name of the program being called.
        :param params: String of parameters to add.
        :param tag: Tag to call the program if different from name. Default: self.name
        :param path: A full path to the program's binary. Default: get from self.name.
        :param cmd: A command string to call the program. Default: build from self.path and self.params.
        """
        self.name = name
        if params is False:
            self.params = dict()
        else:
            self.params = params
        self.param_str = generate_param_str(self.params)
        self.tag = tag
        self.path = path
        self.cmd = cmd
        if not tag:
            self.tag = self.name
        if not path:
            self.path = subprocess.getoutput(f"which {self.name}")
        if not cmd:
            self.cmd = self.generate_cmd()

    def __repr__(self):
        return f"Program '{self.name}' with {len(self.params)} parameter(s)."

    def generate_cmd(self):
        return " ".join([self.path, self.param_str]).strip()

    def add_parameter(self, parameter):
        """
        :param parameter: an instance of the Parameter class
        :return:
        """
        k = getattr(parameter, "key")
        self.params[k] = parameter.value
        self.param_str = generate_param_str(self.params)
        self.cmd = self.generate_cmd()

    def run(self):
        pass

    pass


class Parameter:
    """
    Class holding information for parameters.
    """

    def __init__(
        self,
        key="",
        value="",
        tag=None,
        program=None,
        cmd_string=None,
        description=None,
    ):
        """
        :param key: Key of the parameter, e.g. '-h' for help command.
        :param value: Value of the parameter.
        :param tag: A tag of the parameter.
        :param program: The program to which the parameter belongs to. Must be an instance of the Program class.
        :param cmd_string: String representation of the parameter in a command.
        :param description: description of the parameter.
        """
        self.key = key
        self.program = program
        self.value = value
        self.tag = tag
        self.cmd_string = cmd_string
        self.description = description
        if not self.tag:
            self.tag = self.key
        if not self.cmd_string:
            self.cmd_string = key + " " + str(value)
        self.dict = {key: value}

    def __repr__(self):
        if self.value == "":
            str_ = f"Parameter {self.key} with no value."
        else:
            str_ = f"Parameter {self.key} with value {self.value}."
        if self.description:
            str_ += " Parameter description: " + self.description
        return str_

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def cmd_string(self):
        return self._cmd_string

    @cmd_string.setter
    def cmd_string(self, value):
        self._cmd_string = value

    @property
    def dict(self):
        return self._dict

    @dict.setter
    def dict(self, value):
        self._dict = value

    pass


def generate_param_str(params):
    """
    To-do: imporve this docstring
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
                v = v.dict
                str_ += v + " "
            else:
                str_ += (
                    k + " " + v + " "
                )  # Else we construct the string from the the provided dict.
        param_str = str_
    else:
        # To-do: add more parameters options. List of tuples, List of Parameter instances, etc.
        print("Must provide either a string or a dictionary for the paramaters!")
        raise TypeError
    return param_str.strip()


name_, param_ = "prodigal", "-h"
param = Parameter(param_, description="Help.")
p = Program(name_)
param_i = Parameter("-i", "bioprov/data/genomes/GCF_000010065.1_ASM1006v1_genomic.fna")
param_a = Parameter("-a", "bioprov/data/genomes/GCF_000010065.1_ASM1006v1_genomic.fna")
p.add_parameter(param_i)
p.add_parameter(param_a)
