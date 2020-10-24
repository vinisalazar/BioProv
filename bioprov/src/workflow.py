__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"

"""
Contains the Workflow class and related functions.
"""

import argparse
import pandas as pd
from glob import glob
from bioprov import from_df, config
from bioprov.utils import Warnings
from bioprov.src.main import PresetProgram
from os import path
from tqdm import tqdm


class Workflow:
    """
    Workflow class. Used to build workflows for BioProv command line.

    A workflow runs a series of steps (bioprov.Program) on a set of samples (bioprov.Project).
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
        **kwargs,
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
        :param tag: Tag of the Project being run.
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
        self.default_steps = []  # Must be added by add_step()
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
        self.kwargs = kwargs
        self.sampleset = None
        self.parser = None

        # Only generate sampleset if there is an input and input type
        if self.input and self.input_type:
            _input_types = ("directory", "dataframe")
            assert (
                self.input_type in _input_types
            ), f"Input type '{self.input_type}' is invalid, choose from {_input_types}"
            self.generate_sampleset()

        # Only generate parser if there is a name, description, and steps.
        if all(
            (item is not None for item in (self.name, self.description, self.steps))
        ):
            self.generate_parser()

    def generate_sampleset(self):
        """
        Generate Project instance from input.
        :return: Project instance.
        """
        _generate_sampleset = {
            "dataframe": self._load_dataframe_input,
            "directory": self._load_directory_input,
        }
        self.sampleset = _generate_sampleset[self.input_type]()

    def generate_parser(self):
        parser = argparse.ArgumentParser(
            self.name,
            description=self.description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "-i",
            "--input",
            help=f"""
            Input file, may be a tab delimited file or a directory.\
            If a file, must contain column '{self.index_col}' for sample ID and '{self.file_columns}' for files.\
            See program help for information.
            """,
            required=True,
        )
        parser.add_argument(
            "-c",
            "--cpus",
            help="Default is set in BioProv config (half of the CPUs).",
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
        parser.add_argument(
            "--steps",
            help=f"A comma-delimited string of which steps will be run in the workflow.\nPossible steps:\n{list(self.steps.keys())}",
            default=self.default_steps,
        ),

        self.parser = parser

    def add_step(self, step):
        """
        Updates self.parser and self.steps with an instance of Step.
        :param step: An instance of Step containing a PresetProgram.
        :return:
        """
        assert isinstance(step, Step), Warnings()["incorrect_type"](step, Step)
        if step.default:
            self.default_steps.append(step.name)
        self.steps[step.name] = step
        # Update parser:
        self.generate_parser()

    def run_steps(self, steps_to_run):
        """
        Runs steps for each sample.
        :param steps_to_run: Comma-delimited string of steps to run.
        :return:
        """
        if isinstance(steps_to_run, str):
            steps_to_run = steps_to_run.split(",")
        assert len(
            steps_to_run
        ), f"Invalid steps to run:\n'{steps_to_run}'\nPlease provide a comma-delimited string."
        if self.sampleset is None:
            self.generate_sampleset()
        for k, step in self.steps.items():
            if k in steps_to_run:
                for _, sample in tqdm(self.sampleset.items()):
                    _run = step.run(sample=sample, _print=self.verbose)
                    if not step.runs[
                        str(len(step.runs))
                    ].stderr:  # Add to successes if no standard error.
                        step.successes += 1
            else:
                if self.verbose:
                    print(f"Skipping step '{step.name}'")

    def _sampleset_from_dataframe(self, df):
        """
        Run from_df on dataframe and updates self.sampleset.
        :param df: Instance of pd.DataFrame.
        :return: Updates self.sampleset.
        """
        # Loading samples statement
        print(Warnings()["sample_loading"](len(df)))
        sampleset = from_df(
            df, index_col=self.index_col, file_cols=self.file_columns, tag=self.tag
        )
        return sampleset

    def _load_directory_input(self):
        """
        Generates Project from directory.
        :return: bioprov.Project
        """
        directory = self.input
        file_extensions = self.file_extensions
        file_columns = self.file_columns

        # Make sure directory exists
        assert path.isdir(
            directory
        ), f"Input directory '{directory}' not found. Make sure directory exists."

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
        ), f"No files found in directory '{directory}' with extensions: {file_extensions}"

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
        Generates Project from DataFrame.
        :return: bioprov.Project
        """

        index_col = self.index_col
        input_ = self.input
        file_columns = self.file_columns

        # Assert input file exists
        assert path.isfile(input_), Warnings()["not_exist"]

        # Read input
        df = pd.read_csv(input_, sep=self.sep)

        # Assert index_col exists in df.columns
        assert (
            index_col in df.columns
        ), f"Column '{self.index_col}' is not in input file '{self.input}'. Please check file."

        # Processing files
        if isinstance(file_columns, str):  # Make sure is a LIST
            file_columns = [
                file_columns,
            ]
        elif isinstance(file_columns, tuple):
            file_columns = list(file_columns)
        self.file_columns = file_columns

        # Assert all file columns exists in df.columns
        for col in self.file_columns:
            assert (
                col in df.columns
            ), f"File column '{col}' is not in input file '{self.input}'. Please check file."

        # Check if files exist
        for ix, row in df[file_columns].iterrows():
            for column in file_columns:
                file_ = row[column]
                assert path.isfile(
                    file_
                ), f"File '{file_}' was not found! Make sure all file paths are correct in input file."

        sampleset = self._sampleset_from_dataframe(df)
        return sampleset

    def main(self):
        """
        Parses command-line arguments and runs the workflow.
        :return:
        """
        self.generate_parser()
        args = self.parser.parse_args()
        self.input = args.input
        self.input_type = args.input_type
        steps = args.steps
        self.run_steps(steps)


class Step(PresetProgram):
    """
    Class for holding workflow steps.

    Steps are basically PresetProgram instances but they do not have
    any Sample associated with them, and always generate command strings.

    They have two extra attributes: input_files and output_files.
    """

    def __init__(
        self,
        preset_program,
        default=False,
        description="",
    ):
        super().__init__(
            preset_program.name,
            preset_program.params,
            preset_program.sample,
            preset_program.input_files,
            preset_program.output_files,
            preset_program.preffix_tag,
        )
        self.default = default
        self.description = description
        self.successes = 0
