__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Contains the Program, Parameter and Run class and related functions.

To-do:
    - implement ParameterDict
"""
import datetime
from time import time
from subprocess import Popen, PIPE, getoutput


class Program:
    """
    Class for holding information about programs.
    """

    def __init__(
        self,
        name=None,
        params=None,
        tag=None,
        path=None,
        version=None,
        cmd=None,
        version_param=" -v",
    ):
        """
        :param name: Name of the program being called.
        :param params: Dictionary of parameters.
        :param tag: Tag to call the program if different from name. Default: self.name
        :param path: A full path to the program's binary. Default: get from self.name.
        :param cmd: A command string to call the program. Default: build from self.path and self.params.
        :param version: Version of the program.
        :param version_param: the parameter passed to the program to return the version.
        """
        self.name = name
        self.params = parse_params(params)
        self.param_str = generate_param_str(self.params)
        self.tag = tag
        self.path = path
        self.version = version
        self.cmd = cmd
        self.run_ = Run(self)
        if tag is None:
            self.tag = self.name
        if path is None:
            self.path = getoutput(f"which {self.name}")
        if cmd is None:
            self.cmd = self.generate_cmd()
        if version is None:
            if name is not None:
                self.version = getoutput(self.name + version_param).strip()

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

    def run(self, sample=None, _print=True):
        """
        Runs the process.
        :param sample: An instance of the Sample class
        :param _print: Argument to pass to Run.run()
        :return: An instance of Run class.
        """

        # Update self._run, run self.run() and update self._run again.
        run_ = Run(self, sample=sample)
        self.run_ = run_
        run_.run(_print=_print)
        self.run_ = run_


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
            if self.key is None:
                self.cmd_string = ""
            else:
                if not isinstance(self.value, str):
                    self.value = str(self.value)
                self.cmd_string = self.key + " " + self.value

    def __repr__(self):
        return self.cmd_string
        # # I am leaving this commented for now as I may reimplement it later. Still deciding.
        # if self.value == "":
        #     str_ = f"Parameter {self.key} with no value."
        # else:
        #     str_ = f"Parameter {self.key} with value {self.value}."
        # if self.description is not None:
        #     str_ += " Description: " + f"'{self.description}.'"
        # if self.kind is not None:
        #     str_ += " Kind: " + f"'{self.kind}."
        # return str_

    pass


class Run(Program):
    """
    Class for holding Run information about a selected Program.
    """

    def __init__(self, program=None, params=None, sample=None):
        """
        :param program: An instance of bioprov.Program.
        :param sample: An instance of bioprov.Sample
        """
        if program is None:
            self.program = Program.__init__(self, params)
            self.params = parse_params(params)
        else:
            self.program = program
            self.params = program.params
        self.sample = sample

        # Process status
        self.process = None
        self.stdin = None
        self.stdout = None
        self.stderr = None

        # Time status
        self.start_time = None
        self.end_time = None
        self.duration = None

        # Run status
        self.started = False
        self.finished = False
        self.status = self._finished_to_status(self.finished)

    def __repr__(self):
        str_ = f"Run of Program '{self.program.name}' with {len(self.params)} parameter(s)."
        if self.start_time is not None:
            str_ += f"\nStarted at {self.start_time}."
        if self.end_time is not None:
            str_ += f"\nEnded at {self.end_time}."
        str_ += f"\nStatus is {self.status.lower()}."
        return str_

    @property
    def status(self):
        return self._finished_to_status(self.finished)

    @status.setter
    def status(self, _):
        value = self._finished_to_status(self.finished)
        self._status = value

    @staticmethod
    def _finished_to_status(finished_status):
        """
        :bool finished_status: 
        :return: String representation of status.
        """
        dict_ = {True: "Finished", False: "Pending"}
        return dict_[finished_status]

    def run(self, _sample=None, _print=True):
        """
        Runs process for the Run instance.
        Will update attributes accordingly.
        :type _print: bool
        :param _sample: self.sample
        :return: self.stdout
        """
        if _sample is None:
            _sample = self.sample

        # Declare process and start time
        program_exists = "command not found" not in getoutput(self.program.name)
        assert (
            program_exists
        ), "Cannot find program {}. Make sure it is on your $PATH.".format(self.name)
        if _print:
            str_ = f"Running program '{self.program.name}'"
            if _sample is not None:
                str_ += f" for sample {_sample.name}."
            else:
                str_ += "."
            str_ += "\nCommand is:\n{}".format(self.program.cmd)
            print(str_)
        p = Popen(self.program.cmd, shell=True, stdout=PIPE, stderr=PIPE)
        self.process = p
        self.started, start = True, time()
        self.start_time = datetime.datetime.fromtimestamp(start).strftime("%c")

        # Run process
        (self.stdout, self.stderr) = p.communicate()

        # Update status
        end = time()
        self.end_time = datetime.datetime.fromtimestamp(end).strftime("%c")
        duration = end - start
        duration = str(datetime.timedelta(seconds=duration))
        self.duration = duration
        self.finished = True
        self.status = self._finished_to_status(self.finished)

        return self.stdout


def parse_params(params, program=None):
    """
    Function used to parse parameter input.
    :param params: An instance or iterator of Parameter instances or a dictionary.
    :param program: an instance of Program, if the case.
    :return: Parsed parameters to serve as attribute to a Program or Run instance.
    """
    params_ = dict()
    if isinstance(params, dict):
        for k, v in params.items():
            if isinstance(v, Parameter):
                v.program, v.tag = v.program, v.program
                params_[k] = v
            else:
                params_[k] = Parameter(k, v, program=program)
    elif isinstance(params, (list, tuple)):
        for param in params:
            params_[param.key] = param
    elif isinstance(params, Parameter):
        params.program = program
        params_ = {params.key: params}
    elif params is None:
        pass
    return params_


# Replace 'params' here with ParameterDict, but the above parse_params() will do for now.
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
