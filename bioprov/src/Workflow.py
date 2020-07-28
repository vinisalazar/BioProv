__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Contains the Workflow class and related functions.
"""

import argparse
import pandas as pd
from glob import glob
from bioprov import from_df, config, Sample, Program, Parameter
from bioprov.src.Program import parse_params
from bioprov.utils import warnings
from os import path


class Workflow:
    """
    Workflow class. Used to build workflows for BioProv command line.

    A workflow runs a series of steps (bioprov.Program) on a set of samples (bioprov.SampleSet).
    """

    def __init__(
        self,
        name=None,
        description=None,
        input_=None,
        input_type="dataframe",
        index_col="sample-id",
        file_columns=None,
        file_extensions=None,
        steps=None,
        parser=None,
        tag=None,
        verbose=None,
        threads=None,
        sep="\t",
        **kwargs
    ):
        """
        :param name: Name of the workflow, with no spaces.
        :param description: A brief (one sentence) description of the workflows.
        :param input_: Input of workflow. May be a directory or a tab-delimited file.
        :param input_type: Input type of the workflow. Choose from ('directory', 'dataframe', 'both')
        :param index_col: Name of index column which will define sample names if input_type is 'dataframe'.
        :param file_columns: Name of columns containing files if input_type is 'dataframe'.
                             Name of file tag if input_type is 'directory'.
        :param file_extensions: Extension of files if input_type is 'directory'.
        :param steps: Dictionary mapping step name to a boolean value of whether it runs by default or not.
        :param parser: argparse.ArgumentParser object used to construct the workflow's command-line application.
        :param tag: Tag of the SampleSet being run.
        :param verbose: Verbose output of workflow.
        :param threads: Number of threads in workflow. Defaults to bioprov.config.threads
        :param sep: Separator if input_type is 'dataframe'.
        :param kwargs: Other keyword arguments to be passed to workflow.
        """
        self.name = name
        self.description = description
        self.input = input_
        self.input_type = input_type
        self.index_col = index_col
        self.file_columns = file_columns
        self.file_extensions = file_extensions
        if not steps:
            steps = dict()
        self.steps = steps
        self.parser = parser
        self.tag = tag
        self.verbose = verbose
        self.threads = threads
        self.sep = sep
        self.success = 0
        self.kwargs = kwargs
        self.sampleset = None
        self.parser = None

        # Only generate sampleset if there is an input and input type
        if self.input and self.input_type:
            _input_types = ("directory", "dataframe")
            assert (
                self.input_type in _input_types
            ), "Input type '{}' is invalid, choose from {}".format(
                self.input_type, _input_types
            )
            self.generate_sampleset()

        # Only generate parser if there is a name, description, and steps.
        if all(
            (item is not None for item in (self.name, self.description, self.steps))
        ):
            self.parser = self.generate_parser()

    def generate_sampleset(self):
        """
        Generate SampleSet instance from input.
        :return: SampleSet instance.
        """
        _generate_sampleset = {
            "dataframe": self._load_dataframe_input(),
            "directory": self._load_directory_input(),
        }

        self.sampleset = _generate_sampleset[self.input_type]

    def generate_parser(self):
        parser = argparse.ArgumentParser(self.name, description=self.description)
        parser.add_argument(
            "-i",
            "--input",
            help="""
            Input file, may be a tab delimited file or a directory.\
            If a file, must contain column '{}' for sample ID and '{}' for files.\
            See program help for information.
            """.format(
                self.index_col, self.file_columns
            ),
        )
        parser.add_argument(
            "-t",
            "--threads",
            help="Number of threads. Default is set in BioProv config (half of the threads).",
            default=config.threads,
        )
        parser.add_argument(
            "--verbose",
            help="More verbose output",
            action="store_true",
            default=False,
            required=False,
        )
        parser.add_argument("-t", "--tag", help="A tag for the dataset", required=False)
        return parser

    def add_step(self, parser, step):
        """
        Adds a step to the workflow parser and to the steps attribute.
        :param parser: self.parser
        :param step: A tuple consisting of (str, function, bool), where default is a boolean value.
                     Which defines if the step is by default included in the workflow.
        :return: Updated self.steps and returns parser.
        """
        # Big assert block
        assert (
            len(step) == 3
        ), "Step must be an iterator with only three values, (str, function, bool)"
        name, function, default = step[0], step[1], step[2]
        assert isinstance(default, bool), "'default"

        # Construct argument name
        arg_name = "--skip_" + name
        arg_help = "Whether to skip program '{}' . Default is {}".format(
            name, not default
        )
        actions = {False: "store_true", True: "store_false"}
        arg_action = actions[default]

        # Add argument to parser
        parser.add_argument(
            arg_name, help=arg_help, action=arg_action, default=default, required=False
        )

        self.steps[name] = {"function": function, "default": default}
        return parser

    def _sampleset_from_dataframe(self, df):
        """
        Run from_df on dataframe and updates self.sampleset.
        :param df: Instance of pd.DataFrame.
        :return: Updates self.sampleset.
        """
        # Loading samples statement
        print(warnings["sample_loading"](len(df)))
        sampleset = from_df(
            df, index_col=self.index_col, file_cols=self.file_columns, tag=self.tag
        )
        return sampleset

    def _load_directory_input(self):
        """
        Generates SampleSet from directory.
        :return: bioprov.SampleSet
        """
        directory = self.input
        file_extensions = self.file_extensions
        file_columns = self.file_columns

        # Make sure directory exists
        assert path.isdir(
            directory
        ), "Input directory '{}' not found. Make sure directory exists.".format(
            directory
        )

        # Get files with correct extensions from directory
        if isinstance(file_extensions, str):
            file_extensions = (file_extensions,)
            self.file_extensions = file_extensions
        files = []
        for ext in file_extensions:
            files += glob(path.join(directory, "*." + ext))

        # Make sure we got files
        assert (
            len(files) > 0
        ), "No files found in directory '{}' with extensions: {}".format(
            directory, file_extensions
        )

        # Build dataframe from files
        df = pd.DataFrame(files)
        df.columns = (file_columns,)
        df["sample-id"] = df[file_columns].apply(
            lambda s: path.splitext(path.basename(s))[0]
        )

        sampleset = self._sampleset_from_dataframe(df)
        return sampleset

    def _load_dataframe_input(self):
        """
        Generates SampleSet from DataFrame.
        :return: bioprov.SampleSet
        """

        index_col = self.index_col
        input_ = self.input
        file_columns = self.file_columns

        # Assert block
        assert path.isfile(input_), warnings["not_exist"]

        df = pd.read_csv(input_, sep=self.sep)
        assert (
            index_col in df.columns
        ), "Column '{}' is not in input file '{}'. Please check file.".format(
            self.index_col, self.input
        )

        # Processing files
        if isinstance(file_columns, str):  # Make sure is iterator
            file_columns = (file_columns,)
            self.file_columns = file_columns

        # Check if files exist
        for ix, row in df[file_columns].iterrows():
            for column in file_columns:
                file_ = row[column]
                assert path.isfile(
                    file_
                ), "File '{}' was not found! Make sure all file paths are correct in input file.".format(
                    file_
                )

        sampleset = self._sampleset_from_dataframe(df)
        return sampleset


class WorkflowStep(Program):
    """
    Class for holding a workflow step and related function.

    A WorkflowStep instance inherits from Program and consists of an instance
    of Program with an associated instance of Sample or SampleSet.

    It also possess an attribute 'func' which is used to construct the Program,
    based on the Sample or SampleSet.
    """

    def __init__(
        self,
        program=None,
        params=None,
        sample=None,
        default=True,
        input_files=None,
        output_files=None,
        preffix_tag=None,
    ):
        """
        :param program: Instance of bioprov.Program
        :param params: Dictionary of parameters.
        :param sample: An instance of Sample or SampleSet.
        :param default: Whether to run the step by default.
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
        if program is None:
            self.program = Program.__init__(self, params)
            self.params = parse_params(params)
        else:
            assert isinstance(program, Program), warnings["incorrect_type"](
                program, Program
            )
            self.program = program
            self.params = program.params
        self.sample = sample
        self.default = default
        if input_files is None:
            input_files = dict()
        if output_files is None:
            output_files = dict()
        self.input_files = input_files
        self.output_files = output_files

        if self.sample is not None:
            self.create_func(preffix_tag)

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
            param = Parameter(key=k, value=str(self.sample.files[tag]), kind="input")
            self.program.add_parameter(param)

    def _parse_output_files(self, preffix_tag=None):
        """
        Adds output files to self.sample and self.program.
        :param preffix_tag: A tag of an input file which will be used as preffix to specify output files.0
        :return: Updates self.program with the output files as parameters and0
                 updates the 'files' attribute of self.sample.files.
        """
        if preffix_tag is None:
            preffix = path.join("./", self.sample.name)
        else:
            # Check if it is in sample
            try:
                preffix, _ = path.splitext(str(self.sample.files[preffix_tag]))
            except KeyError:
                raise Exception(
                    "Key '{}' not found in files dictionary of sample '{}':\n'{}'".format(
                        preffix_tag, self.sample.name, self.sample.files
                    )
                )
        try:
            for key, (tag, suffix) in self.output_files.items():
                self.sample.add_files({tag: preffix + suffix})
                param = Parameter(
                    key=key, value=str(self.sample.files[tag]), kind="output"
                )
                self.program.add_parameter(param)
        except ValueError:
            raise Exception(
                "Please check the output files dictionary:\n'{}'\n"
                "It must have the following structure: key: (tag, suffix)."
            )

    def create_func(self, preffix_tag=None):
        """
        :param preffix_tag: Argument to be passed to self._parse_output_files()
        :return: Creates Program function for Sample.
        """
        assert isinstance(self.sample, Sample), warnings["incorrect_type"](
            self.sample, Sample
        )
        assert isinstance(self.program, Program), warnings["incorrect_type"](
            self.program, Program
        )

        self._parse_input_files()
        self._parse_output_files(preffix_tag)


def prodigal(sample):
    _prodigal = WorkflowStep(
        program=Program("prodigal"),
        params=None,
        sample=sample,
        default=True,
        input_files={"-i": "assembly"},
        output_files={
            "-a": ("proteins", "_proteins.faa"),
            "-d": ("genes", "_genes.fna"),
            "-s": ("scores", "_scores.fna"),
        },
        preffix_tag="assembly",
    )
    _prodigal.create_func()

    return _prodigal
