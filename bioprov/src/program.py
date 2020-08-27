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
from bioprov.src.sample import Sample
from bioprov.utils import warnings
from os import path
from subprocess import Popen, PIPE, getoutput
from time import time


class Program:
    """
    Class for holding information about programs.
    """

    def __init__(
        self,
        name=None,
        params=None,
        tag=None,
        path_to_bin=None,
        version=None,
        cmd=None,
        version_param=" -v",
    ):
        """
        :param name: Name of the program being called.
        :param params: Dictionary of parameters.
        :param tag: Tag to call the program if different from name. Default: self.name
        :param path_to_bin: A full path to the program's binary. Default: get from self.name.
        :param cmd: A command string to call the program. Default: build from self.path and self.params.
        :param version: Version of the program.
        :param version_param: the parameter passed to the program to return the version.
        """
        self.name = name
        self.params = parse_params(params)
        self.param_str = generate_param_str(self.params)
        self.tag = tag
        self.path = path_to_bin
        self.version = version
        self.cmd = cmd
        self.run_ = Run(self)
        self._getoutput = getoutput("which {}".format(self.name))
        self.found = (
            "command not found" not in self._getoutput and self._getoutput != ""
        )
        if tag is None:
            self.tag = self.name
        if path_to_bin is None:
            self.path = self._getoutput
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
        run_.run(_print=_print)
        self.run_ = run_
        return run_


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
        keyword_argument=True,
        position=-1,
    ):
        """
        :param key: Key of the parameter, e.g. '-h' for help command.
        :param value: Value of the parameter.
        :param tag: A tag of the parameter.
        :param program: The program to which the parameter belongs to. Must be an instance of the Program class.
        :param cmd_string: String representation of the parameter in a command.
        :param description: description of the parameter.
        :param kind: Kind of parameter. May be 'input', 'output', 'misc', or None.
        :param keyword_argument: Whether the parameter is a keyword argument.
                                 Keyword arguments have a key, which is used to build
                                 the program's command. If this is false, it is assumed
                                 that the parameter is a positional argument, and 'position'
                                 will indicate it's index if the command line was split as a list.
        :param position: Index of insertion of parameter in command-line if it is a positional argument.
        """
        self.key = key
        self.program = program
        self.value = value
        self.tag = tag
        self.cmd_string = cmd_string
        self.description = description
        self.kind = kind
        self.dict = {key: value}
        self.keyword_argument = keyword_argument
        self.position = position

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
                if keyword_argument:
                    self.cmd_string = self.key + " " + self.value
                else:
                    self.cmd_string = self.value

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
        assert (
            self.program.found
        ), "Cannot find program {}. Make sure it is on your $PATH.".format(
            self.program.name
        )
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


class PresetProgram(Program):
    """
    Class for holding a preset program and related functions.

    A WorkflowStep instance inherits from Program and consists of an instance
    of Program with an associated instance of Sample or Project.
    """

    def __init__(
        self,
        program=None,
        params=None,
        sample=None,
        input_files=None,
        output_files=None,
        preffix_tag=None,
        generate_cmd=False,
    ):
        """
        :param program: Instance of bioprov.Program
        :param params: Dictionary of parameters.
        :param sample: An instance of Sample or Project.
        :param input_files: A dictionary consisting of Parameter keys as keys and a File.tag
                            as value, where File.tag is a string that must be a key in
                            self.sample.files with a corresponding existing file.
        :param output_files: A dictionary consisting of Parameter keys as keys and a tuple
                             consisting of (File.tag, suffix) as value.
                             File.tag will become a key in self.sample.files and the its value
                             will be the sample_name + suffix.
        :param preffix_tag: A value in the input_files argument, which corresponds
                            to a key in self.sample.files. All file names of output
                            files will be stemmed from this file, hence 'preffix'.
        :param generate_cmd: Generates generic command, independent of sample.
        """
        if program is None:
            self.program = Program.__init__(self, params)
            self.params = parse_params(params)
        else:
            assert isinstance(program, Program), warnings["incorrect_type"](
                program, Program
            )
            self.program = program
            self.params = program.params
        self.name = self.program.name
        self.sample = sample
        if input_files is None:
            input_files = dict()
        if output_files is None:
            output_files = dict()
        self.input_files = input_files
        self.output_files = output_files
        self.preffix_tag = preffix_tag
        self.generic_cmd = None
        self.ready = False

        if generate_cmd:
            self.generate_cmd()

        if self.sample is not None:
            self.create_func(self.preffix_tag)

    def __repr__(self):
        str_ = "PresetProgram '{0}'".format(self.program.name)
        if self.generic_cmd:
            str_ += " with the following command for each sample:\n'{0}'".format(
                self.generic_cmd
            )
        return str_

    def _parse_input_files(self):
        """
        Checks if input files exist and adds them to self.program.
        :return: Updates self.program with the input files as parameters.
        """
        for k, tag in self.input_files.items():
            # Check if it is in sample
            try:
                file_ = self.sample.files[tag]
            except KeyError:
                raise Exception(
                    "Key '{}' not found in files dictionary of sample '{}':\n'{}'".format(
                        tag, self.sample.name, self.sample.files
                    )
                )

            # If in sample, check if it exists
            assert file_.exists, warnings["not_exist"](file_)

            # Finally, add file to program as a parameter.
            param = Parameter(
                key=k, value=str(self.sample.files[tag]), kind="input", tag=tag
            )
            self.program.add_parameter(param)

    def _parse_output_files(self):
        """
        Adds output files to self.sample and self.program.
        :return: Updates self.program with the output files as parameters and0
                 updates the 'files' attribute of self.sample.files.
        """
        if self.preffix_tag is None:
            preffix = path.join("./", self.sample.name)
        else:
            # Check if it is in sample
            try:
                preffix, _ = path.splitext(str(self.sample.files[self.preffix_tag]))
            except KeyError:
                raise Exception(
                    "Key '{}' not found in files dictionary of sample '{}':\n'{}'".format(
                        self.preffix_tag, self.sample.name, self.sample.files
                    )
                )
        try:
            for key, (tag, suffix) in self.output_files.items():
                self.sample.add_files({tag: preffix + suffix})
                param = Parameter(
                    key=key, value=str(self.sample.files[tag]), kind="output", tag=tag
                )
                self.program.add_parameter(param)
        except ValueError:
            raise Exception(
                "Please check the output files dictionary:\n'{}'\n"
                "It must have the following structure: key: (tag, suffix)."
            )

    def create_func(self, sample, preffix_tag=None):
        """
        :param sample: Instance of Sample to create the function for.
        :param preffix_tag: Argument to be passed to self._parse_output_files()
        :return: Creates Program function for Sample.
        """
        # Set new sample
        self.sample = sample

        # Set preffix tag
        if preffix_tag is not None:
            self.preffix_tag = preffix_tag

        # Validate current state
        self.validate_sample()
        self.validate_program()

        # Parse files
        self._parse_input_files()
        self._parse_output_files()

        # Set ready state
        self.ready = True

    def validate_sample(self):
        """
        Checks type of self.sample.
        :return:
        """
        assert isinstance(self.sample, Sample), warnings["incorrect_type"](
            self.sample, Sample
        )

    def validate_program(self):
        """
        Checks type of self.program
        :return:
        """
        assert isinstance(self.program, Program), warnings["incorrect_type"](
            self.program, Program
        )

    def generate_cmd(self, from_files=True):
        """
        Generates a wildcard command string, independent of samples.
        :param from_files: Generate command from self.input_files and self.output_files (recommended) If False,
        will generate from parameter dictionary instead.
        :return: Updates self.generic_cmd.
        """
        self.validate_program()

        # Add parameters to command
        params_ = self.params
        for k, parameter in params_.items():
            # Replace file names with place holders.
            if parameter.kind in ("input", "output"):
                parameter.value = "sample.files['{}']".format(parameter.tag)
            else:
                pass
        # Now parse resulting output
        generic_cmd = generate_param_str(params_)

        # Update self
        self.generic_cmd = generic_cmd

    def run(self, sample=None, _print=True, preffix_tag=None):
        """
        Runs PresetProgram for sample.
        :param sample: Instance of bioprov.Sample.
        :param _print: Whether to print more output.
        :param preffix_tag: Preffix tag to self.create_func()
        :return:
        """
        if sample is None:
            sample = self.sample
        if preffix_tag is None:
            preffix_tag = self.preffix_tag
        if not self.ready:
            self.create_func(sample, preffix_tag)
        self.program.run_ = self.program.run(sample=sample, _print=_print)
        return self.program.run_


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
    str_, pos_args = "", []  # Positional arguments are added in the last bit
    if not params:
        return str_
    elif params:
        for k, v in params.items():
            # If is a Parameter class instance, we inherit the corresponding tags.
            if isinstance(v, Parameter):
                if v.keyword_argument:
                    str_ += v.cmd_string + " "
                else:
                    pos_args.append(v)
            else:
                str_ += (
                    k + " " + v + " "
                )  # Else we construct the string from the the provided dict.
        param_str = str_.strip()
    else:
        # To-do: add more parameters options. List of tuples, List of Parameter instances, etc.
        print("Must provide either a string or a dictionary for the parameters!")
        raise TypeError
    # Add positional arguments
    split_str = param_str.split()
    for arg in pos_args:
        split_str.insert(arg.position, arg.value)
    param_str = " ".join(split_str).strip()

    return param_str
