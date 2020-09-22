__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.2"

"""
Contains the Program, Parameter and Run class and related functions.

Contains the Sample and Project classes and related functions.

To-do:
    - implement ParameterDict
"""
import datetime
import json
import pandas as pd
from bioprov.utils import Warnings, serializer
from bioprov.src.files import File, SeqFile
from coolname import generate_slug
from os import path
from pathlib import Path
from subprocess import Popen, PIPE, getoutput
from time import time
from types import GeneratorType


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
    ):
        """
        :param name: Name of the program being called.
        :param params: Dictionary of parameters.
        :param tag: Tag to call the program if different from name. Default: self.name
        :param path_to_bin: A full _path to the program's binary. Default: get from self.name.
        :param cmd: A command string to call the program. Default: build from self._path and self.params.
        :param version: Version of the program.
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

    def __repr__(self):
        return f"Program '{self.name}' with {len(self.params)} parameter(s)."

    def generate_cmd(self):
        """
        Generates command string to execute.

        :return: command string
        """
        cmd = " ".join([self.path, self.param_str]).strip()
        self.cmd = cmd
        return cmd

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
        self.generate_cmd()
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
        self.run_ = run_.run(_sample=sample, _print=True)
        return run_

    def serializer(self):
        serial_out = self.__dict__
        if "run_" in serial_out.keys():
            del serial_out["run_"]
        return serializer(serial_out)


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


class Run:
    """
    Class for holding Run information about a selected Program.
    """

    def __init__(self, program=None, params=None, sample=None):
        """
        :param program: An instance of bioprov.Program.
        :param sample: An instance of bioprov.Sample
        """
        self.program = program
        if self.program is None:
            self.program = Program.__init__(self.program, params)
            self.params = parse_params(params)
        else:
            self.program = program
            self.params = program.params

        assert isinstance(self.program, Program), Warnings()["incorrect_type"](
            self.program, Program
        )
        self.sample = sample
        self.cmd = self.program.cmd

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

        return self

    def serializer(self):
        # The following lines prevent RecursionError
        serial_out = self.__dict__
        for key in ("sample", "program"):
            if key in serial_out.keys():
                del serial_out[key]
        return serializer(serial_out)


class PresetProgram(Program):
    """
    Class for holding a preset program and related functions.

    A WorkflowStep instance inherits from Program and consists of an instance
    of Program with an associated instance of Sample or Project.
    """

    def __init__(
        self,
        name=None,
        params=None,
        sample=None,
        input_files=None,
        output_files=None,
        preffix_tag=None,
    ):
        """
        :param name: Instance of bioprov.Program
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
        """
        super().__init__(name, params)
        self.sample = sample
        if input_files is None:
            input_files = dict()
        if output_files is None:
            output_files = dict()
        self.input_files = input_files
        self.output_files = output_files
        self.preffix_tag = preffix_tag
        self.ready = False
        self.generate_cmd()

        if self.sample is not None:
            self.create_func(sample=self.sample, preffix_tag=self.preffix_tag)

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
            assert file_.exists, Warnings()["not_exist"](file_)

            # Finally, add file to program as a parameter.
            param = Parameter(
                key=k, value=str(self.sample.files[tag]), kind="input", tag=tag
            )
            self.add_parameter(param)

    def _parse_output_files(self):
        """
        Adds output files to self.sample and self.
        :return: Updates self with the output files as parameters and
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
                self.add_parameter(param)
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
        assert isinstance(self.sample, Sample), Warnings()["incorrect_type"](
            self.sample, Sample
        )

    def validate_program(self):
        """
        Checks type of self
        :return:
        """
        assert isinstance(self, Program), Warnings()["incorrect_type"](self, Program)

    def generate_cmd(self, from_files=True):
        """
        Generates a wildcard command string, independent of samples.
        :param from_files: Generate command from self.input_files and self.output_files (recommended) If False,
        will generate from parameter dictionary instead.
        :return: Updates self.cmd.
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
        generic_cmd = " ".join([self.path, generate_param_str(params_)]).strip()

        # Update self
        self.cmd = generic_cmd
        return generic_cmd

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
        # Update self._run, run self.run() and update self._run again.
        Program.run(self, sample=sample, _print=_print)


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


def add_programs(object_, programs):
    """
    Adds program(s) to object. Must be an instance or iterable of bioprov.Program.
    :param object_: A bioprov.Sample or Project instance.
    :param programs: bioprov.Program iterator or instance, value where key is the program name
                     and value is a bp.Program instance.
    :return: Updates self by adding the programs to object.
    """

    # Assert it is adding to correct object
    assert isinstance(
        object_, (Sample, Project)
    ), "Can't add file to type '{}'. Can only add file to Sample or Project object.".format(
        type(object_)
    )

    # If a single item, make into tuple and assert correct type
    if isinstance(programs, Program):
        programs = (programs,)
    else:
        for item in programs:
            assert isinstance(item, Program), Warnings()["incorrect_type"](
                item, Program
            )

    # Set 'programs' attribute in object if None
    if object_.programs is None:
        object_.programs = dict()

    # Finally, append programs to object_.programs
    for program in programs:
        object_.programs[program.name] = program


def add_runs(object_, runs):
    """
    Adds run(s) to object. Must be an instance or iterable of bioprov.Run.
    :param object_: A bioprov.Sample or Project instance.
    :param runs: bioprov.Run iterator or instance or dict with key, value where key is the run name
                     and value is a bp.Run instance.
    :return: Updates self by adding the runs to object.
    """

    # Assert it is adding to correct object
    assert isinstance(
        object_, (Sample, Project)
    ), "Can't add file to type '{}'. Can only add file to Sample or Project object.".format(
        type(object_)
    )

    # If a single item, make into tuple and assert correct type
    if isinstance(runs, Run):
        runs = (runs,)
    else:
        for item in runs:
            assert isinstance(item, Run), Warnings()["incorrect_type"](item, Run)

    # Set 'runs' attribute in object if None
    if object_.runs is None:
        object_.runs = dict()

    # Finally, append runs to object_.runs
    for run in runs:
        object_.runs[str(len(object_.runs) + 1)] = run


"""
Sample block starts here.
 
This block was contained in a separate module but was moved here to prevent circular import problems.
"""


class Sample:
    """
    Class for holding sample information and related files and programs.
    """

    def __init__(self, name=None, tag=None, files=None, attributes=None):
        """
        :param name:  Sample name or ID.
        :param tag: optional tag describing the sample.
        :param files: Dictionary of files associated with the sample.
        :param attributes: Dictionary of any other attributes associated with the sample.
        """
        if isinstance(name, str):
            name = name.replace(" ", "_")  # No space, will use it for filenames.

        self.name = name
        self.tag = tag
        if isinstance(files, dict):
            files_ = dict()
            for k, v in files.items():
                if isinstance(v, File):
                    files_[k] = v
                else:  # if not a File instance, create one.
                    files_[k] = File(path=v, tag=k)
            files = files_
        elif files is None:
            files = dict()
        self.files = files
        if attributes is not None:
            assert isinstance(attributes, dict)
        else:
            attributes = dict()
        self.attributes = attributes
        self._programs = None
        self._runs = None

    def __repr__(self):
        str_ = f"Sample {self.name} with {len(self.files)} file(s)."
        return str_

    def __getitem__(self, item):
        return self.files[item]

    def __setitem__(self, key, value):
        assert isinstance(
            value, (File, SeqFile)
        ), f"To create file in sample, must be either a bioprov.File or bioprov.SequenceFile instance."
        self.files[key] = value

    def add_programs(self, programs):
        """
        Adds program(s) to self. Must be an instance or iterable of bioprov.Program.
        :param programs: bioprov.Program iterator or instance, value where key is the program name
                         and value is a bp.Program instance.
        :return: Updates self by adding the programs to object.
        """
        add_programs(self, programs)

    def add_files(self, files):
        """
        Sample method to add files.
        :param files: See input to add_files function.
        :return: Adds files to Sample
        """
        add_files(self, files)

    def add_runs(self, runs):
        """
        Sample method to add runs.
        :param runs: See input to add_runs function.
        :return: Adds runs to Sample
        """
        add_runs(self, runs)

    def serializer(self):
        """
        Custom serializer for Sample class. Serializes runs, programs, and files attributes.
        :return:
        """
        return serializer(self)

    def run_programs(self, _print=True):
        """
        Runs self._programs in order.
        :return:
        """
        if len(self.programs) >= 1:
            for _, p in self.programs.items():
                self._run_program(p, _print=_print)
        else:
            print("No programs to run for Sample '{}'".format(self.name))

    def _run_program(self, program, _print=True):
        """
        Run a Program or PresetProgram on Sample.
        :param program: An instance of bioprov.Program or PresetProgram
        :param _print: Whether to print output of Program.
        :return: Runs the program for Sample.
        """
        run = program.run(sample=self, _print=print)

        if program not in self.programs:
            self.programs[program.name] = program
        if run not in self.runs:
            self.runs[str(len(self.runs) + 1)] = run

    @property
    def runs(self):
        if self._runs is None:
            self._runs = dict()
        return self._runs

    @property
    def programs(self):
        if self._programs is None:
            self._programs = dict()
        return self._programs

    def to_json(self, _path=None, _print=True):
        """
        Exports the Sample as JSON. Similar to Project.to_json()
        :param _path: JSON output file path.
        :param _print: Whether to print if the file was created correctly.
        :return:
        """
        return to_json(self, self.serializer(), _path, _print=_print)


class Project:
    """
    Class which holds a dictionary of Sample instances, where each key is the sample name.
    """

    def __init__(self, samples=None, tag=None):
        """
        Initiates the object by creating a sample dictionary.
        :param samples: An iterator of Sample objects.
        :param tag: A tag to describe the Project.
        """
        self.tag = tag
        self.files = dict()
        samples = self.is_iterator(
            samples
        )  # Checks if `samples` is a valid constructor.
        samples = self.build_sample_dict(samples)
        self._samples = samples

    def __len__(self):
        return len(self._samples)

    def __repr__(self):
        return f"Project with {len(self._samples)} samples."

    def __getitem__(self, item):
        try:
            value = self._samples[item]
            return value
        except KeyError:
            keys = self.keys()
            print(
                f"Sample {item} not in Project.\n",
                "Check the following keys:\n",
                "\n".join(keys),
            )

    def __setitem__(self, key, value):
        self._samples[key] = value

    def keys(self):
        return self._samples.keys()

    def values(self):
        return self._samples.values()

    def items(self):
        return self._samples.items()

    def add_files(self, files):
        """
        Project method to add files.
        :param files: See input to add_files function.
        :return: Adds files to Project
        """
        add_files(self, files)

    @staticmethod
    def is_sample_and_name(sample):
        """
        Checks if an object is of the Sample class.
        Name the sample if it isn't named.
        :param sample: an object of the Sample class.
        :return:
        """
        # Check class
        assert isinstance(sample, Sample), f"{sample} is not a valid Sample object!"

        # Name
        if sample.name is None:
            slug = generate_slug(2)
            sample.name = slug
            print("No sample name set. Setting random name: {}".format(sample.name))

        return sample

    @staticmethod
    def is_iterator(constructor):
        """
        Checks if the constructor passed is a valid iterable, or None.
        :param constructor: constructor object used to build a Project instance.
        :return:.
        """
        assert type(constructor) in (
            list,
            dict,
            tuple,
            GeneratorType,
            type(None),
        ), f"'samples' must be an iterator of Sample instances."

        return constructor

    @staticmethod
    def build_sample_dict(constructor):
        """
        Build sample dictionary from passed constructor.
        :param constructor: Iterable or NoneType
        :return: dictionary of sample instances.
        """
        samples = dict()
        if constructor is None:
            return samples

        if isinstance(constructor, dict):
            constructor = list(constructor.values())

        for sample in constructor:
            sample = Project.is_sample_and_name(sample)
            samples[sample.name] = sample

        return samples

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, value):
        self._samples = self.build_sample_dict(value)

    def serializer(self):
        return serializer(self)

    def to_json(self, _path=None, _print=True):
        """
        Exports the Project as JSON. Similar to Sample.to_json()
        :param _path: JSON output file _path.
        :param _print: Whether to print if the file was created correctly.
        :return:
        """
        return to_json(self, self.serializer(), _path, _print=_print)


def add_files(object_, files):
    """
    Adds file(s) to object. Must be a dict or an instance or iterable of bioprov.File.
    :param object_: A Sample or Project instance.
    :param files: bioprov.File list, instance or dict with key, value where value is the file _path.
    :return: Updates self by adding the file to object.
    """

    # Assert it is adding to correct object
    assert isinstance(
        object_, (Sample, Project)
    ), "Can't add file to type '{}'. Can only add file to Sample or Project object.".format(
        type(object_)
    )

    # If it is a dict, we convert to File instances
    if isinstance(files, dict):
        files_ = dict()
        for k, v in files.items():
            # This is to convert JSON files.
            if isinstance(v, dict):
                files_[k] = File(v["path"], v["tag"])
            else:
                files_[k] = File(v, tag=k)

        files = files_

    # If it is an iterable of File instances, transform to a dict
    elif isinstance(files, list):
        files = {file.name: file for file in files}

    # If it is a single item, also transform to dict
    elif isinstance(files, File):
        files = {files.tag: files}  # Grabs by tag because it is File.name by default

    # Here files must be a dictionary of File instances
    for k, v in files.items():
        if k in object_.files.keys():
            print(f"Updating file {k} with value {v}.")
        object_.files[k] = v


def to_json(object_, dictionary, _path=None, _print=True):
    """
    Exports the Sample or Project as JSON.
    :return: Writes JSON output
    """
    if _path is None:
        assert object_.tag is not None
        _path = f"./{object_.tag}.json"

    if "json" not in object_.files.keys():
        object_.add_files({"json": _path})

    return write_json(dictionary, _path, _print=_print)


def from_json(json_file, kind="Sample"):
    """
    Imports Sample or Project from JSON file.
    :param json_file: A JSON file created by Sample.to_json()
    :param kind: Whether to create a Sample or Project instance.
    :return: a Sample or Project instance.
    """
    assert kind in ("Sample", "Project"), "Must specify 'Sample' or 'Project'."
    d = json_to_dict(json_file)
    if "name" in d.keys():  # This checks whether the file is a Sample or Project
        kind = "Sample"  # To-do: must be improved.
    else:
        kind = "Project"
    if kind == "Sample":
        sample_ = dict_to_sample(d)
        return sample_
    elif kind == "Project":
        samples = dict()
        for k, v in d["_samples"].items():
            samples[k] = dict_to_sample(v)

        # Create Project
        project = Project(samples=samples, tag=d["tag"])
        project.add_files(d["files"])

        return project


def from_df(
    df,
    index_col=0,
    file_cols=None,
    sequencefile_cols=None,
    tag=None,
    source_file=None,
    import_data=False,
):
    """
    Pandas-like function to build a Project object.

    By default, assumes the sample names or ids are in the first column,
        else they should be specified by 'index_col' arg.
    '''
    samples = from_df(df_path, sep="\t")

    type(samples)  # bioprov.Sample.Project.

    You can select columns to be added as Files or SequenceFile instances.
    '''
    :param df: A pandas DataFrame
    :param index_col: A column to be used as index. Must be in df_path.columns.
                        If int is passed, will get it from columns.
    :param file_cols: Columns containing Files.
    :param sequencefile_cols: Columns containing SequenceFiles.
    :param tag: A tag to describe the Project.
    :param source_file: The source file used to read the dataframe.
    :param import_data: Whether to import data when importing SequenceFiles
    :return: a Project instance
    """
    df_ = df.copy()
    if isinstance(index_col, int):
        index_col = df_.columns[index_col]
    assert (
        index_col in df_.columns
    ), f"Index column '{index_col}' not present in columns!"
    df_.set_index(index_col, inplace=True)

    samples = dict()
    attribute_cols = [
        i for i in df_.columns if i not in (file_cols, sequencefile_cols, index_col)
    ]
    for ix, row in df_.iterrows():
        sample = Sample(name=ix)

        for arg, type_ in zip((file_cols, sequencefile_cols), ("file", "sequencefile")):
            if arg is not None:
                if isinstance(arg, str):  # If a string is passed,
                    arg = (arg,)  # we must make a list/tuple so we can iterate.
                for column in arg:
                    if type_ == "file":
                        sample.add_files(File(path=row[column], tag=column))
                    elif type_ == "sequencefile":
                        sample.add_files(
                            SeqFile(
                                path=row[column], tag=column, import_records=import_data
                            )
                        )
        if (
            len(attribute_cols) > 0
        ):  # Here we check by len() instead of none because it is a list.
            for attr_ in attribute_cols:
                sample.attributes[attr_] = row[attr_]
        samples[ix] = sample

    samples = Project(samples, tag=tag)
    if source_file:
        samples.add_files({"project_csv": source_file})

    return samples

    pass


def read_csv(df_path, sep=",", **kwargs):
    """
    :param df_path: Path of dataframe.
    :param sep: Separator of dataframe.
    :param kwargs: Any kwargs to be passed to from_df()
    :return: A Project instance.
    """
    df = pd.read_csv(df_path, sep=sep)
    sampleset = from_df(df, source_file=df_path, **kwargs)
    return sampleset


def json_to_dict(json_file):
    """
    Reads dict from a JSON file.
    :param json_file: A JSON file created by Sample.to_json()
    :return: a dictionary (input to dict_to_sample())
    """
    with open(json_file) as f:
        dict_ = json.load(f)
    return dict_


def dict_to_sample(json_dict):
    """
    Converts a JSON dictionary to a sample instance.
    :param json_dict: output of sample_from_json.
    :return: a Sample instance.
    """
    sample_ = Sample()
    for attr, value in json_dict.items():

        # Don't try to create instances if values are not dictionaries
        if value is not None:
            # Create File instances
            if attr == "files":
                for tag, file in value.items():
                    if file is not None:
                        if "format" in file.keys():
                            if file["format"] in SeqFile.seqfile_formats:
                                value[tag] = SeqFile(path=file["path"])
                        else:
                            value[tag] = File(file["path"])
                        for attr_, value_ in file.items():
                            if getattr(value[tag], attr_, value_) is None:
                                setattr(value[tag], attr_, value_)

            # Create Run instances
            if attr == "_runs" and value:
                for tag, run in value.items():
                    value[tag] = Run(Program())
                    for attr_, value_ in run.items():
                        setattr(value[tag], attr_, value_)
                    sample_.add_runs(value[tag])

            # Create Program instances
            if attr == "_programs":
                for tag, program in value.items():
                    value[tag] = Program()
                    for attr_, value_ in program.items():
                        setattr(value[tag], attr_, value_)
                    sample_.add_programs(value[tag])

            setattr(sample_, attr, value)

    return sample_


def write_json(dict_, _path, _print=True):
    """
    Writes dictionary to JSON file.
    :param dict_: JSON dictionary.
    :param _path: String with _path to JSON file.
    :param _print: Whether to print if the file was successfully created.
    :return: Writes JSON file
    """
    with open(_path, "w") as f:
        json.dump(dict_, f, indent=3)

    if _print:
        if Path(_path).exists():
            print(f"Created JSON file at {_path}.")
        else:
            print(f"Could not create JSON file for {_path}.")
