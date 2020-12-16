__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"

"""

Main source module. Contains the main BioProv classes.

Activity classes:
    - Program
    - Parameter
    - Run
    
    
Entity classes:
    - Project
    - Sample

This class also contains functions to read and write objects in JSON and tab-delimited formats.

"""

import datetime
import json
import logging
import tempfile
from collections import OrderedDict
from collections import deque
from os import path
from pathlib import Path
from subprocess import Popen, PIPE, getoutput
from time import time
from types import GeneratorType

import pandas as pd
from coolname import generate_slug
from prov.model import ProvEntity, ProvBundle, Namespace
from tinydb import Query

from bioprov import config
from bioprov.src.config import Environment
from bioprov.src.files import File, SeqFile, Directory, deserialize_files_dict
from bioprov.utils import (
    Warnings,
    serializer,
    serializer_filter,
    dict_to_sha1,
    create_logger,
)


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
        self.cmd = cmd
        self.params = parse_params(params)
        self.param_str = generate_param_str(self.params)
        self.tag = tag
        self.path = path_to_bin
        self.version = version
        self._getoutput = getoutput(f"which {self.name}")
        self.found = (
            "command not found" not in self._getoutput
            and self._getoutput != ""
            and not self._getoutput.startswith("which: no")
        )
        self._runs = None
        if tag is None:
            self.tag = self.name
        if path_to_bin is None:
            self.path = self._getoutput
        if cmd is None:
            self.cmd = self.generate_cmd()

    def __repr__(self):
        return f"Program '{self.name}' with {len(self.params)} parameter(s)."

    @property
    def runs(self):
        if self._runs is None:
            self._runs = dict()
        return self._runs

    @runs.setter
    def runs(self, value):
        self._runs = value

    def add_runs(self, runs):
        """
        Sample method to add runs.
        :param runs: See input to add_runs function.
        :return: Adds runs to Sample
        """
        _add_runs(self, runs)

    def generate_cmd(self):
        """
        Generates command string to execute.

        :return: command string
        """
        cmd = " ".join([self.path, self.param_str]).strip()
        self.cmd = cmd
        return cmd

    def add_parameter(self, parameter, _generate_cmd=True):
        """
        Adds a parameter to the current instance and updates the command.

        :param parameter: an instance of the Parameter class.
        :param _generate_cmd: Refreshes self.cmd when a Parameter is added.

        :return: Updates self.params and self.cmd if _generate_cmd is True.
        """
        assert isinstance(parameter, Parameter), Warnings()["incorrect_type"](
            parameter, Parameter
        )
        k, v = parameter.key, parameter.value
        self.params[k] = parameter
        self.param_str = generate_param_str(self.params)
        config.logger.debug(
            f"Added parameter {k} with value '{v}' to program {self.name}"
        )  # no cover
        if _generate_cmd:
            self.generate_cmd()

    def run(self, sample=None):
        """
        Runs the process.
        :param sample: An instance of the Sample class
        :return: An instance of Run class.
        """
        # Creates Run instance with self
        run_ = Run(self, sample=sample)
        run_.run(_sample=sample)
        self.add_runs(run_)
        return run_

    def serializer(self):
        keys = [
            "sample",
        ]
        return serializer_filter(self, keys)


def deserialize_programs_dict(programs_dict, sample):
    """
    Deserialize programs from JSON format

    :param programs_dict: dictionary of serialized Programs in JSON format
    :param sample: instance of bioprov.Sample
    :return: dictionary of Program instances
    """
    deserialized_programs = dict()
    for tag, program in programs_dict.items():
        deserialized_programs[tag] = Program(program["name"])
        for program_attr_, program_value_ in program.items():
            # Create Parameter attributes
            if program_attr_ == "params" and program_value_:
                for key, param in program_value_.items():
                    parameter = Parameter()
                    for param_attr_, param_value_ in param.items():
                        setattr(parameter, param_attr_, param_value_)
                    deserialized_programs[tag].add_parameter(parameter)
            elif program_attr_ == "_runs" and program_value_:
                deserialize_runs_dict(
                    program_value_, deserialized_programs, tag, sample
                )
            else:
                setattr(deserialized_programs[tag], program_attr_, program_value_)

    return deserialized_programs


class Parameter:
    """
    Class holding information for parameters.
    """

    def __init__(
        self,
        key=None,
        value="",
        tag=None,
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
        return f"Parameter with command string '{self.cmd_string}'"

    def serializer(self):
        keys = [
            "position",
        ]
        return serializer_filter(self, keys)


class Run:
    """
    Class for holding Run information about a selected Program.
    """

    def __init__(self, program, sample=None):
        """
        :param program: An instance of bioprov.Program.
        :param sample: An instance of bioprov.Sample
        """
        assert isinstance(program, Program), Warnings()["incorrect_type"](
            program, Program
        )
        self.program = program
        self.cmd = self.program.cmd
        self.params = self.program.params
        self.sample = sample

        # Process status
        self.process = None
        self.stdin = None
        self.stdout = None
        self.stderr = None

        # This parameter will suppress from writing stdout if it is too long.
        self._auto_suppress_stdout = True

        # Time status
        self.start_time = None
        self.end_time = None
        self.duration = None

        # Run status
        self.started = False
        self.finished = False
        self.status = self._finished_to_status(self.finished)

        # User who ran the task
        self.user = config.user
        self.env = config.env.env_hash

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
        self._status = self._finished_to_status(self.finished)
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @staticmethod
    def _finished_to_status(finished_status):
        """
        :bool finished_status:
        :return: String representation of status.
        """
        dict_ = {True: "Finished", False: "Pending"}
        return dict_[finished_status]

    def run(self, _sample=None):
        """
        Runs process for the Run instance.
        Will update attributes accordingly.
        :param _sample: self.sample
        :return: self
        """
        if _sample is None:
            _sample = self.sample

        # Declare process and start time
        assert (
            self.program.found
        ), f"Cannot find program {self.program.name}. Make sure it is on your $PATH."

        # Print block
        str_ = f"Running program '{self.program.name}'"
        if _sample is not None:
            str_ += f" for sample {_sample.name}."
        else:
            str_ += "."

        # Pretty printing of commands
        split_ = self.program.cmd.split()
        if len(self.program.cmd) > 80:
            if len(split_) % 2 == 1:
                bin_, *fmt_cmd = split_
                last = ""
            else:
                bin_, *fmt_cmd, last = split_  # no cover
            it = iter(fmt_cmd)
            fmt_cmd = zip(it, it)
            fmt_cmd = " \\ \n".join(
                [bin_] + ["\t" + i[0] + " " + i[1] for i in fmt_cmd] + ["\t" + last]
            )
            str_ += f"\nCommand is:\n{fmt_cmd}\n"
        else:
            str_ += f"\nCommand is:\n{self.program.cmd}\n"

        str_ = str_.strip()
        if str_.endswith("\\"):
            str_ = str_[:-1]
        config.logger.info(str_)

        p = Popen(self.program.cmd, shell=True, stdout=PIPE, stderr=PIPE)
        self.process = p
        self.started, start = True, time()
        self.start_time = datetime.datetime.fromtimestamp(start).strftime("%c")

        # Run process
        (self.stdout, self.stderr) = p.communicate()
        self.stdout, self.stderr = (
            self.stdout.decode("utf-8"),
            self.stderr.decode("utf-8"),
        )

        # Update status
        end = time()
        self.end_time = datetime.datetime.fromtimestamp(end).strftime("%c")
        duration = end - start
        duration = str(datetime.timedelta(seconds=duration))
        self.duration = duration
        self.finished = True
        self._status = self._finished_to_status(self.finished)

        if not self._auto_suppress_stdout:
            config.logger.debug(self.stdout)  # no cover
        config.logger.debug(self.stderr)  # no cover

        return self

    def serializer(self):
        # Cannot apply bioprov.utils.serializer_filter to this one
        serial_out = self.__dict__.copy()
        for key in ("stdout", "program", "sample", "params"):
            if key in serial_out.keys():
                if key == "stdout":
                    if (
                        serial_out[key] is not None
                        and len(serial_out[key]) > 5000
                        and self._auto_suppress_stdout
                    ):
                        serial_out[key] = None
                else:
                    del serial_out[key]

        serial_out = serializer(serial_out)
        return serial_out


def deserialize_runs_dict(runs_dict, programs_dict, tag, sample):

    # TODO: replace sample for object when implementing Project.programs

    """
    Deserialize runs in JSON format.

    :param runs_dict: dictionary of Runs in JSON format.
    :param programs_dict: dictionary of Program instances to be updated.
    :param tag: Tag of each program.
    :param sample: Sample to be updated.
    :return:
    """
    for run_tag_, run_ in runs_dict.items():
        runs_dict[run_tag_] = Run(programs_dict[tag], sample=sample)
        for run_attr_, run_value_ in run_.items():
            setattr(runs_dict[run_tag_], run_attr_, run_value_)
        programs_dict[tag].add_runs(runs_dict[run_tag_])


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
        extra_flags=None,
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
        :param extra_flags: A list of command line parameters (strings), known as flags or
                            switches, to add to the program's command.
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
        self.extra_flags = extra_flags
        self.ready = False

        if self.sample is not None:
            self.create_func(sample=self.sample, preffix_tag=self.preffix_tag)

        if self.extra_flags is not None:
            _extra_flags = [Parameter(key=flag) for flag in self.extra_flags]
            for _flag in _extra_flags:
                self.add_parameter(_flag)

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
                    f"Key '{tag}' not found in files dictionary of sample '{self.sample.name}':\n'{self.sample.files}'."
                    f"\nPlease specify a valid input tag."
                )

            # If in sample, check if it exists
            assert file_.exists, Warnings()["not_exist"](file_)

            # Finally, add file to program as a parameter.
            param = Parameter(
                key=k, value=str(self.sample.files[tag]), kind="input", tag=tag
            )
            self.add_parameter(param, _generate_cmd=False)

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
                    f"Key '{self.preffix_tag}' not found in files dictionary of sample '{self.sample.name}':\n"
                    f"'{self.sample.files}'"
                )
        try:
            for key, (tag, suffix) in self.output_files.items():
                self.sample.add_files(
                    {
                        tag: preffix + suffix,
                    }
                )
                param = Parameter(
                    key=key, value=str(self.sample.files[tag]), kind="output", tag=tag
                )
                self.add_parameter(param, _generate_cmd=False)
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

        # Add self to sample automatically
        self.sample.add_programs(self)

        # Set ready state
        self.ready = True
        self.generate_cmd()

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

    def generate_cmd(self):
        """
        TODO: improve this function

        Generates a wildcard command string, independent of samples.
        :return: Updates self.cmd.
        """
        self.validate_program()

        # Add parameters to command
        params_ = self.params
        for k, parameter in params_.items():
            # Replace file names with place holders.
            if parameter.kind in ("input", "output"):
                try:
                    parameter.value = str(self.sample.files[f"{parameter.tag}"])
                except AttributeError:
                    config.logger.warning("Warning: no sample associated with program.")
                    pass  # Suppress bug for now.
            else:
                pass
        # Now parse resulting output
        generic_cmd = " ".join([self.path, generate_param_str(params_)]).strip()

        # Update self
        self.cmd = generic_cmd
        return generic_cmd

    def run(self, sample=None, preffix_tag=None):
        """
        Runs PresetProgram for sample.
        :param sample: Instance of bioprov.Sample.
        :param preffix_tag: Preffix tag to self.create_func()
        :return:
        """
        if sample is None:
            sample = self.sample
        if preffix_tag is None:
            preffix_tag = self.preffix_tag

        self.create_func(sample, preffix_tag)
        run_ = Run(self, sample=sample)
        run_.run(_sample=sample)
        self.add_runs(run_)
        return run_


def parse_params(params):
    """
    Function used to parse parameter input.
    :param params: An instance or iterator of Parameter instances or a dictionary.
    :return: Parsed parameters to serve as attribute to a Program or Run instance.
    """
    params_ = OrderedDict()
    if isinstance(params, dict):
        for k, v in params.items():
            if isinstance(v, Parameter):
                params_[k] = v
            else:
                params_[k] = Parameter(k, v)
    elif isinstance(params, (list, tuple)):
        for param in params:
            params_[param.key] = param
    elif isinstance(params, Parameter):
        params_ = {params.key: params}
    elif params is None:
        pass
    return params_


# Replace 'params' here with ParameterDict, but the above parse_params() will do for now.
def generate_param_str(params):
    """
    TODO: improve this docstring
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
        # TODO: add more parameters options. List of tuples, List of Parameter instances, etc.
        config.logger.error(
            "Must provide either a string or a dictionary for the parameters!"
        )
        raise TypeError
    # Add positional arguments
    split_str = param_str.split()
    for arg in pos_args:
        split_str.insert(arg.position, arg.value)
    param_str = " ".join(split_str).strip()

    return param_str


def _add_programs(object_, programs):
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
    ), f"Can't add file to type '{type(object_)}'. Can only add file to Sample or Project object."

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

    object_.auto_update_db()


def _add_runs(object_, runs):
    """
    Adds run(s) to object. Must be an instance or iterable of bioprov.Run.
    :param object_: A bioprov.Sample or Project instance.
    :param runs: bioprov.Run iterator or instance or dict with key, value where key is the run name
                     and value is a bp.Run instance.
    :return: Updates self by adding the runs to object.
    """

    # Assert it is adding to correct object
    assert isinstance(object_, Program), Warnings()["incorrect_type"](object_, Program)

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

    def __init__(
        self, name=None, tag=None, files=None, directory=None, attributes=None
    ):
        """
        :param name:  Sample name or ID.
        :param tag: optional tag describing the sample.
        :param files: Dictionary of files associated with the sample.
        :param directory: A bioprov.Directory associated with the sample
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
        self._directory = directory
        if attributes is not None:
            assert isinstance(attributes, dict)
        else:
            attributes = dict()
        self.attributes = attributes
        self.programs = OrderedDict()
        self.project = None

        # This is an attribute used by the src.prov module
        self.namespace_preffix = f"samples:{self.name}"
        self.files_namespace_preffix = None

    def auto_update_db(self):
        if self.project is not None:
            self.project.auto_update_db()

    def __repr__(self):
        str_ = f"Sample '{self.name}' with {len(self.files)} file(s)."
        return str_

    def __getitem__(self, key):
        return self.files[key]

    def __delitem__(self, key):
        del self.files[key]

    def __setitem__(self, key, value):
        assert isinstance(
            value, (File, SeqFile)
        ), f"To create file in sample, must be either a bioprov.File or bioprov.SequenceFile instance."
        self.files[key] = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    @property
    def directory(self):
        if self._directory is None and self.files:
            key, file = next(iter(self.files.items()))
            directory = Directory(file.directory, tag=key)
            self._directory = directory
        return self._directory

    @directory.setter
    def directory(self, value):
        if isinstance(value, (str, Path)):
            value = Directory(value)
        self._directory = value

    def add_programs(self, programs):
        """
        Adds program(s) to self. Must be an instance or iterable of bioprov.Program.
        :param programs: bioprov.Program iterator or instance, value where key is the program name
                         and value is a bp.Program instance.
        :return: Updates self by adding the programs to object.
        """
        _add_programs(self, programs)

    def add_files(self, files):
        """
        Sample method to add files.
        :param files: See input to add_files function.
        :return: Adds files to Sample
        """
        _add_files(self, files)

    def serializer(self):
        """
        Custom serializer for Sample class. Serializes runs, programs, and files attributes.
        :return:
        """
        keys = ["files_namespace_preffix", "project"]
        return serializer_filter(self, keys)

    def run_programs(self):
        """
        Runs self._programs in order.
        :return:
        """
        _run_programs(self)

    def _run_program(self, program):
        """
        Runs program for self.
        :param program: bioprov.Program or bioprov.PresetProgram.
        :return: Runs Program and updates self.
        """
        _run_program(self, program)

    def to_json(self, _path=None):
        """
        Exports the Sample as JSON. Similar to Project.to_json()
        :param _path: JSON output file path.
        :return:
        """
        return to_json(self, self.serializer(), _path)

    def to_series(self):
        """
        Creates a pd.Series object from the sample files and attributes.

        :return: pd.Series
        """
        series = {}

        # Can't apply serializer_filter here.
        keys = ["files_namespace_preffix", "namespace_preffix", "_programs", "project"]
        modified_dict = self.__dict__.copy()
        for key in keys:
            try:
                del modified_dict[key]
            except KeyError:
                pass

        for k, v in modified_dict.items():
            if v is None or not v:
                continue
            if isinstance(v, dict) and len(v) > 0:
                for k_, v_ in v.items():
                    series[k_] = v_
            else:
                series[k] = v

        return pd.Series(series)


def _run_program(_object, program):
    """
    Runs program for _object.

    :param _object: bioprov.Project or bioprov.Sample
    :param program: bioprov.Program or bioprov.PresetProgram.
    :return: Runs Program and updates _object.
    """
    if program not in _object.programs.keys():
        _object.add_programs(program)
    program.run(sample=_object)
    _object.auto_update_db()


def _run_programs(_object):
    """
    Runs programs in order.

    :param _object: bioprov.Project or bioprov.Sample
    :return:
    """
    if len(_object.programs) >= 1:
        for _, p in _object.programs.items():
            # noinspection PyProtectedMember
            _object._run_program(p)
    else:
        config.logger.warning(f"No programs to run for {_object}")


class Project:
    """
    Class which holds a dictionary of Sample instances, where each key is the sample name.
    """

    def __init__(
        self,
        tag=None,
        samples=None,
        db=None,
        auto_update=False,
        log_to_file=False,
    ):
        """
        Initiates the object by creating a sample dictionary.
        :param samples: An iterator of Sample objects.
        :param tag: A tag to describe the Project.
        :param db: path to TinyDB to store project in JSON format.
        :param auto_update: Whether to auto_update the BioProvDB record.
                            Disabled by default.
        :param log_to_file: Whether to log the Project to a File. You can define this later with
                            the self.start_logging() method.
        """
        if tag is None:
            slug = generate_slug(2)
            config.logger.warning(
                f"No Project tag was set. Generated random tag: '{slug}'."
            )
            tag = slug
        self.tag = tag.replace(" ", "_")
        self._name = self.tag
        self.files = dict()
        self.programs = OrderedDict()
        samples = self.is_iterator(
            samples
        )  # Checks if `samples` is a valid constructor.
        samples = self.build_sample_dict(samples)
        self._samples = samples

        # environments are stored based on the user name
        # avoid duplicated user names!
        self.users = {config.user: {config.env.env_hash: config.env}}

        # PROV attributes
        self._entity = None
        self._bundle = None
        self._namespace_preffix = f"project:{self.tag}"
        self.files_namespace_preffix = None

        # Hash and db attributes
        self._sha1 = dict_to_sha1(self.serializer())
        self.auto_update = auto_update
        if db is None:
            db = config.db
        self.db = db

        # Log attributes
        self.log_to_file = log_to_file
        self.log_file = None
        self.logger = None
        if self.log_to_file:
            self.start_logging()

    def __len__(self):
        return len(self._samples)

    def __repr__(self):
        return f"Project '{self.tag}' with {len(self)} samples"

    def __getitem__(self, item):
        try:
            value = self._samples[item]
            return value
        except KeyError:
            config.logger.error(
                f"Sample {item} not in Project.\n" f"Check the following keys:" " ",
                "\n  ".join(self.keys),
            )

    def __setitem__(self, key, value):
        self._samples[key] = value

    def __delitem__(self, key):
        del self._samples[key]

    @property
    def namespace_preffix(self):
        self._namespace_preffix = f"project:{str(self)}"
        return self._namespace_preffix

    def keys(self):
        return self._samples.keys()

    def values(self):
        return self._samples.values()

    def items(self):
        return self._samples.items()

    @property
    def name(self):
        self._name = self.tag
        return self._name

    @property
    def sha1(self):
        keys = ("_sha1",)
        new_hash = dict_to_sha1(serializer_filter(self, keys))
        if new_hash != self._sha1:
            self._sha1 = new_hash
            self.auto_update_db()
        return self._sha1

    @sha1.setter
    def sha1(self, value):
        self._sha1 = value

    @property
    def entity(self):
        if self._entity is None:
            self._entity = ProvEntity(self._bundle, identifier=f"project:{self}")
        return self._entity

    @entity.setter
    def entity(self, value):
        self._entity = value

    @property
    def bundle(self):
        if self._bundle is None:
            self._bundle = ProvBundle()
        return self._bundle

    @bundle.setter
    def bundle(self, bundle):
        self._bundle = bundle

    def update_db(self, db=None):
        if db is None:
            db = self.db
        result, query = self.query_db(db)
        if result:
            db.update(self.serializer(), query.tag == self.tag)
        else:
            config.logger.info(f"Inserting new project '{self.tag}' in {db.db_path}")
            db.insert(self.serializer())

    def auto_update_db(self):
        """
        Updates the database if auto_update is True.
        """
        if self.auto_update:
            self.update_db()

    def query_db(self, db=None):
        if db is None:
            db = self.db
        query = Query()
        result = db.search(query.tag == self.tag)
        return result, query

    def _update_envs(self):
        if config.env.env_hash not in self.users.values():
            self.users[config.user][config.env.env_hash] = {
                config.env.env_hash: config.env
            }

    def replace_paths(self, old_terms, new, warnings=False):
        """
        Runs File.replace_path(old_terms, new) on all Files in the project and each Sample.

        For more information see File.replace_path() documentation.

        :param old_terms: old terms to be replaced.
        :param new: new term.
        :param warnings: whether to activate warnings.

        :return: Updates all Files associated with self.
        """
        for _, file in self.files.items():
            file.replace_path(old_terms, new, warnings)

        for _, sample in self.items():
            for _, file in sample.files.items():
                file.replace_path(old_terms, new, warnings)

    def start_logging(
        self, log_file=None, level=logging.INFO, _custom_start_message=None
    ):
        """
        Starts logging Project to File.

        :param log_file: Path to log file. If None will be defined automatically.
        :param level: Logging level.
        :param _custom_start_message: Custom starting message to start the log.
        :return: Creates logger attributes and refreshes bp.config.logger
        """
        if log_file is None:
            log_file = f"{self.tag}.log"
        self.log_file = log_file
        self.logger = config.logger = create_logger(level, self.log_file, self.tag)
        if _custom_start_message is None:
            _custom_start_message = f"Starting log for project '{self.tag}'."

        self.logger.info(_custom_start_message)

        self.add_files(File(self.log_file, tag="log"))
        self.logger.info(f"Writing log to {self.files['log']}")
        self.logger.info(f"Loading {len(self)} samples.")

    def add_files(self, files):
        """
        Adds Files to self.files. See documentation to bioprov.src.main.add_files().

        :param files: Dict, list, or File instance.
        :return: Updates self.files
        """
        _add_files(self, files)

    def add_programs(self, programs):
        """
        Add programs to self. See documentation to bioprov.src.main.Progarm
        :param programs: Dict, list, or Program instance.
        :return: Updates self.programs
        """
        _add_programs(self, programs)

    def run_programs(self):
        """
        Runs all programs in self.programs in order.

        :return:
        """
        _run_programs(self)

    def _run_program(self, program=None):
        """
        Runs program for self.

        :param program: bioprov.Program or bioprov.PresetProgram.
        :return: Runs Program and updates self.
        """
        _run_program(self, program)

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
            config.logger.warning(
                f"No sample name set. Setting random name: {sample.name}"
            )

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

    def build_sample_dict(self, constructor):
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
            samples[sample.name].project = self

        return samples

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, value):
        self._samples = self.build_sample_dict(value)

    def serializer(self):
        return serializer(self)

    def to_json(self, _path=None):
        """
        Exports the Project as JSON. Similar to Sample.to_json()
        :param _path: JSON output file _path.
        :return:
        """
        return to_json(self, self.serializer(), _path)

    def to_df(self):
        """
        Creates a Pandas DataFrame from Sample files and attributes.
        :return: pd.DataFrame
        """
        rows = [sample.to_series() for _, sample in self.items()]
        df = pd.concat(rows, axis=1).T
        df.set_index("name", inplace=True)
        return df

    def to_csv(self, path_=None, sep=",", **kwargs):
        """
        Writes a tab-delimited file of sample files and attributes using the to_df method.
        :return:
        """

        # automatic file extensions FTW
        def get_ext(sep_):
            ext_dict = {",": ".csv", "\t": ".tsv"}
            try:
                ext_ = ext_dict[sep_]
            except KeyError:
                ext_ = ".txt"
            return ext_

        ext = get_ext(sep)

        # default output is working directory
        if path_ is None:
            path_ = "./" + self.tag + ext

        # avoid duplicated extensions
        path_ = path_.replace(ext + ext, ext)

        # finally, write
        df = self.to_df()
        df.to_csv(path_, sep=sep, **kwargs)


def _add_files(object_, files):
    """
    Adds file(s) to object. Must be a dict or an instance or iterable of bioprov.File.
    :param object_: A Sample or Project instance.
    :param files: bioprov.File list, instance or dict with key, value where value is the file _path.
    :return: Updates self by adding the file to object.
    """

    # Assert it is adding to correct object
    assert isinstance(
        object_, (Sample, Project)
    ), f"Can't add file to type '{type(object_)}'. Can only add file to Sample or Project object."

    # If it is a dict, we convert to File instances
    if isinstance(files, dict):
        files_ = dict()
        for k, v in files.items():

            # This is to convert JSON files.
            if isinstance(v, dict):
                if v["path"].endswith("/"):
                    files_[k] = Directory(v["path"], v["tag"])
                else:
                    files_[k] = File(v["path"], v["tag"])

            # This is the usual flow
            else:
                if str(v).endswith("/"):
                    files_[k] = Directory(v, tag=k)
                else:
                    files_[k] = File(v, tag=k)

        files = files_

    # If it is an iterable of File instances, transform to a dict
    elif isinstance(files, list):
        files = {file.name: file for file in files}

    # If it is a single item, also transform to dict
    elif isinstance(files, (File, Directory)):
        files = {files.tag: files}  # Grabs by tag because it is File.name by default

    # Here 'files' must be a dictionary of File or Directory instances
    for k, v in files.items():
        if k in object_.files.keys():
            config.logger.info(f"Updating file {k} with value {v}.")
        object_.files[k] = v

    object_.auto_update_db()


def to_json(object_, dictionary, _path=None):
    """
    Exports the Sample or Project as JSON.
    :return: Writes JSON output
    """
    if _path is None:
        assert object_.tag is not None, "Please tag your project to export it!"
        _path = f"./{object_.tag}.json"

    if "json" not in object_.files.keys():
        object_.add_files({"json": _path})

    return write_json(dictionary, _path)


def from_json(json_file, kind="Project", replace_path=None, replace_home=False):
    """
    Imports Sample or Project from JSON file.

    :param json_file: A JSON file created by Sample.to_json()
    :param kind: Whether to create a Sample or Project instance.
    :param replace_path: A tuple or list with two strings.
                          The first will be the old path to be replaced,
                          and the second will be the new.
    :param replace_home: If True, will run replace_path automatically for previous HOME paths.

    :return: a Sample or Project instance.
    """
    # TODO: reimplement replace_path as a Project method.

    assert kind in ("Sample", "Project"), "Must specify 'Sample' or 'Project'."
    d = json_to_dict(json_file)

    # will probably deprecate this
    if "name" in d.keys():  # This checks whether the file is a Sample or Project
        kind = "Sample"  # TODO: must be improved.
    else:
        kind = "Project"
    if kind == "Sample":
        sample_ = dict_to_sample(d)
        return sample_

    # kind == "Sample" will be deprecated
    # this function should become the following block
    elif kind == "Project":

        if replace_path:
            assert (
                all(type(i) is str for i in replace_path) and len(replace_path) == 2
            ), "You must prove a tuple or list with two strings to 'replace_path'"
            # We want the old terms in a container
            replace_path = ((replace_path[0],), replace_path[1])

        # set some defaults, but if _replace_home
        # is False, they won't be used.
        HOME, other_HOME_variables = None, []
        if replace_home:
            HOME = str(Path.home())

        samples = dict()

        try:
            for k, v in d["_samples"].items():
                samples[k] = dict_to_sample(v)
        except KeyError:
            pass

        # Create Project
        project = Project(tag=d["tag"], samples=samples)

        # Deserializing and adding project files and programs
        try:
            deserialized_files = deserialize_files_dict(d["files"])
            deque((project.add_files(file_) for file_ in deserialized_files.values()))
            deserialized_programs = deserialize_programs_dict(d["programs"], project)
            deque(
                (
                    project.add_programs(program_)
                    for program_ in deserialized_programs.values()
                )
            )
        except KeyError:
            pass

        try:
            for user, env in d["users"].items():
                for env_hash, env_dict in env.items():
                    try:
                        project.users[user][env_hash] = Environment()
                    except KeyError:
                        project.users[user] = dict()
                        project.users[user][env_hash] = Environment()
                    for env_attr_, attr_value_ in env_dict.items():
                        if env_attr_ == "env_namespace":
                            attr_value_ = Namespace(
                                "envs", str(project.users[user][env_hash])
                            )
                        if replace_home:
                            if env_attr_ == "env_dict":
                                other_HOME_variables.append(attr_value_["HOME"])
                        setattr(project.users[user][env_hash], env_attr_, attr_value_)
        except KeyError:
            pass

        if replace_home:
            project.replace_paths(other_HOME_variables, HOME, warnings=True)

        if replace_path:
            config.logger.info(
                "Replacing paths:"
                f"\tOld:\t{replace_path[0][0]}"
                f"\tNew:\t{replace_path[1]}"
            )
            project.replace_paths(replace_path[0], replace_path[1], warnings=True)

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

    samples = Project(tag=tag, samples=samples)
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
    project = from_df(df, source_file=df_path, **kwargs)
    return project


def json_to_dict(json_file):
    """
    Reads dict from a JSON file.
    :param json_file: A JSON file created by Sample.to_json()
    :return: a dictionary (input to dict_to_sample())
    """
    with open(json_file) as f:
        dict_ = json.load(f)
    return dict_


# this function is hideous. it must be improved.
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
            if attr == "files":

                # Adding files
                deserialized_files = deserialize_files_dict(value)
                deque(
                    (sample_.add_files(file_) for file_ in deserialized_files.values())
                )

            # Create Program instances
            elif attr == "programs":
                deserialized_programs = deserialize_programs_dict(value, sample_)
                deque(
                    (
                        sample_.add_programs(program_)
                        for program_ in deserialized_programs.values()
                    )
                )
            else:
                setattr(sample_, attr, value)

    return sample_


def write_json(dict_, _path):
    """
    Writes dictionary to JSON file.
    :param dict_: JSON dictionary.
    :param _path: String with _path to JSON file.
    :return: Writes JSON file.
    """
    with open(_path, "w") as f:
        json.dump(dict_, f, indent=3)

    if Path(_path).exists():
        config.logger.info(f"Created JSON file at {_path}.")
    else:
        config.logger.info(f"Could not create JSON file for {_path}.")


def load_project(tag):
    """
    Loads Project from the BioProvDatabase set in the config.

    :param tag: Tag of the Project to be loaded.
    :return: Instance of Project.
    """
    assert (
        len(config.db) > 0
    ), f"Project not found. Database at '{config.db_path}' is empty"

    query = Query()
    try:
        result = config.db.search(query.tag == tag)[0]
    except (IndexError, KeyError):
        config.logger.error(f"Project not found in database at {config.db_path}")
        return

    with tempfile.NamedTemporaryFile() as f:
        f.write(bytes(json.dumps(result), "utf-8"))
        project = from_json(f.name)

    return project
