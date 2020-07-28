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
from bioprov import from_df, default_config
from bioprov.utils import warnings
from bioprov.src.program import PresetProgram
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
        :param steps: Dictionary of steps. May also receive a list, tuple or None.
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
        self.steps = (
            dict()
        )  # Will only update if isinstance(steps, (list, dict, tuple):

        # Parse steps arg - dict
        if isinstance(steps, dict):
            for _, step in steps.items():
                self.add_step(step)

        # Parse steps arg - list
        elif isinstance(steps, (list, tuple)):
            self.steps = dict()
            for step in steps:
                self.add_step(step)

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
            self.generate_parser()

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
            default=default_config.threads,
        )
        parser.add_argument(
            "--verbose",
            help="More verbose output",
            action="store_true",
            default=False,
            required=False,
        )
        parser.add_argument("-t", "--tag", help="A tag for the dataset", required=False)
        self.parser = parser

    def add_step(self, step):
        """
        Updates self.parser and self.steps with an instance of Step.
        :param step: An instance of Step containing a PresetProgram.
        :return:
        """
        assert isinstance(step, Step), warnings["incorrect_type"](step, Step)

        # Construct argument name and action
        # for parser based on whether it's a default step
        # If default is True, store_false and use '--skip'
        # If default is False, store_true and use '--run'
        arg_action = {False: "store_true", True: "store_false"}
        action = {False: "run", True: "skip"}
        arg_suffix = "--{}_".format(action)

        # Get name and default state from step
        name, default = step.name, step.default
        arg_name = arg_suffix[default] + name
        arg_help = "Whether to {} program '{}'. Default is {}".format(
            action, name, default
        )
        self.parser.add_argument(
            arg_name, help=arg_help, action=arg_action, default=default, required=False,
        )
        self.steps[name] = step

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


class Step(PresetProgram):
    """
    Class for holding workflow steps.

    Steps are basically PresetProgram instances but they do not have
    any Sample associated with them, and alawys generate command strings.

    They have two extra attributes:
    """

    def __init__(
        self,
        program,
        params,
        input_files,
        output_files,
        preffix_tag,
        default=False,
        description="",
    ):
        super().__init__(
            program=program,
            params=params,
            input_files=input_files,
            output_files=output_files,
            preffix_tag=preffix_tag,
            generate_cmd=True,
        )
        self.name = program.name
        self.default = default
        self.description = description
