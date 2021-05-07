__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.24"
__doc__ = """
Module containing preset workflows created with the Workflow class.
"""


from bioprov.programs import blastn, prodigal
from bioprov.src.workflow import Workflow, Step

# Kaiju WF imports. These will be removed later
import argparse
import logging
from os import path, getcwd, mkdir

import pandas as pd
from tqdm import tqdm

from bioprov import config, from_df, Sample
from bioprov.programs import kaiju, kaiju2table
from bioprov.utils import Warnings, tax_ranks


def blastn_alignment(**kwargs):

    _blastn_alignment = Workflow(
        name="blastn",
        description="Align nucleotide data to a reference database with BLASTN.",
        input_type="dataframe",
        index_col="sample-id",
        file_columns="query",
        **kwargs,
    )

    try:
        _blastn_alignment.db = kwargs["db"]
    except KeyError:
        _blastn_alignment.db = None

    blastn_preset = blastn(db=_blastn_alignment.db)

    _blastn_alignment.add_step(Step(blastn_preset, default=True))

    # Workflow specific arguments must be added AFTER the steps.
    # That is because adding a Step updates the parser with the default arguments
    # of the Workflow class.

    _blastn_alignment.parser.add_argument(
        "-db",
        "--database",
        help="BLASTn reference database. Must be a valid BLAST database created with the `makeblastdb` command.",
        required=True,
    )

    return _blastn_alignment


def genome_annotation(**kwargs):
    _genome_annotation = Workflow(
        name="genome_annotation",
        description="Genome annotation with Prodigal, Prokka and the COG database.",
        input_type="dataframe",
        index_col="sample-id",
        file_columns="assembly",
        **kwargs,
    )

    # Create steps from preset programs.
    prodigal_preset, prokka_preset = (prodigal(), None)  # prokka()
    steps = [
        Step(prodigal_preset, default=True),
        # Step(prokka_preset, default=False),
    ]

    # Add steps to parser
    for _step in steps:
        _genome_annotation.add_step(_step)

    return _genome_annotation


class KaijuWorkflow:
    """
    Class holding the KaijuWorkflow main function and parser.
    """

    description = (
        "Run Kaiju on metagenomic data and create reports for taxonomic ranks."
    )

    def __init__(self):
        pass

    @staticmethod
    def main(
        input_file,
        output_path=None,
        kaijudb=None,
        nodes=None,
        names=None,
        threads=config.threads,
        _tag=None,
        verbose=False,
        resume=True,
        kaiju_params="",
        kaiju2table_params="",
    ):
        """
        Main function to run the Kaiju workflow.

        :param input_file: Input tab delimited file with the columns: 'sample-id', 'R1', 'R2'
        :param output_path: Directory to create Kaiju output files.
        :param kaijudb: Kaiju database file.
        :param nodes: Kaiju nodes file.
        :param names: Kaiju names file.
        :param threads: Number of threads to use with Kaiju.
        :param _tag: Tag for Project.
        :param verbose: Verbose output.
        :param resume: Check for existing files and skip running Kaiju for them.
        :param kaiju_params: Parameter string to add to Kaiju command.
        :param kaiju2table_params: Parameter string to add to kaiju2table command.
        :return:
        """
        # Asserting files exist
        for file_ in (input_file, kaijudb, nodes, names):
            assert path.isfile(file_), Warnings()["not_exist"](file_)

        # Asserting columns are correct
        df = pd.read_csv(input_file, sep="\t")
        for column in ("sample-id", "R1", "R2"):
            assert (
                column in df.columns
            ), f"Column '{column}' not present in {input_file}."

        # Assert all files exist
        for ix, row in df[["R1", "R2"]].iterrows():
            for column in ("R1", "R2"):
                file_ = row[column]
                assert path.isfile(
                    file_
                ), f"File '{file_}' was not found! Make sure all file paths are correct in input file."

        logging.warning(Warnings()["sample_loading"](len(df)))

        # Create BioProv Project
        ss = from_df(df, index_col="sample-id", file_cols=("R1", "R2"), tag=_tag)

        success, skip = 0, 0

        sample: Sample
        for k, sample in tqdm(ss.items()):
            kaiju_ = kaiju(
                sample,
                output_path=output_path,
                kaijudb=kaijudb,
                nodes=nodes,
                threads=threads,
                add_param_str=kaiju_params,
            )

            # If resume is 'on', will check for existing files and skip if needed.
            if resume and sample.files["kaiju_output"].exists:
                skip += 1
                continue

            kaiju_run = kaiju_.run(sample, _print=verbose)
            if verbose:
                print(kaiju_run)

            # Create reports for each rank (this is much faster than running Kaiju)
            if not verbose:
                print("Creating Kaiju reports.")
            for rank in tax_ranks:
                if verbose:
                    print(f"Creating report for {rank} rank.")
                kaiju2table_ = kaiju2table(
                    _sample=sample,
                    rank=rank,
                    nodes=nodes,
                    names=names,
                    add_param_str=kaiju2table_params,
                )
                kaiju2table_.run(sample)

            all_files_exist = False
            for k_, v in sample.files.items():
                if not path.isfile(str(v)):
                    all_files_exist = False
                    break
                else:
                    all_files_exist = True

            if all_files_exist:
                success += 1

        ss.to_json()
        print(Warnings()["number_success"](success, len(df)))
        print(Warnings()["number_skip"](skip))

    @classmethod
    def parser(cls):
        """
        Parser for the Kaiju workflow.
        :return: instance of argparse.ArgumentParser.
        """
        _parser = argparse.ArgumentParser(
            "kaiju",
            description=KaijuWorkflow.description,
        )
        _parser.add_argument(
            "-i",
            "--input",
            help=(
                "Input file, a tab delimited file which must contain three columns: 'sample-id', 'R1', and 'R2',\
                containing respectively sample IDs, _path to forward reads and _path to reverse reads."
            ),
            required=True,
            type=str,
        )
        _parser.add_argument(
            "-o",
            "--output_directory",
            help="Output directory to create Kaiju files. Default is directory of input file.",
            required=False,
            default=None,
        )
        _parser.add_argument(
            "-db",
            "--kaiju_db",
            help="Kaiju database file.",
            required=True,
        )
        _parser.add_argument(
            "-no",
            "--nodes",
            help="NCBI Taxonomy nodes.dmp file required to run Kaiju.",
            required=True,
        )
        _parser.add_argument(
            "-na",
            "--names",
            help="NCBI Taxonomy names.dmp file required to run Kaiju2Table.",
            required=True,
        )
        _parser.add_argument(
            "--kaiju_params",
            help="Parameter string to be added to Kaiju command.",
            required=False,
            default="",
        )
        _parser.add_argument(
            "--kaiju2table_params",
            help="Parameter string to be added to Kaiju2table command.",
            required=False,
            default="",
        )
        _parser.add_argument(
            "-t", "--tag", help="A tag for the dataset", required=False
        )
        _parser.add_argument(
            "-v",
            "--verbose",
            help="More verbose output",
            action="store_true",
            default=False,
            required=False,
        )
        _parser.add_argument(
            "-p",
            "--threads",
            help="Number of threads. Default is set in BioProv config (half of the threads).",
            default=config.threads,
        )
        return _parser


class WorkflowOptionsParser:
    """
    Class for parsing command-line options.
    """

    def __init__(self):
        pass

    @staticmethod
    def _blastn_alignment(kwargs, steps):
        """
        Runs blastn alignment workflow
        :return:
        """
        main = blastn_alignment(**kwargs)
        main.run_steps(steps)

    @staticmethod
    def _genome_annotation(kwargs, steps):
        """
        Runs genome annotation workflow
        :return:
        """
        main = genome_annotation(**kwargs)
        main.run_steps(steps)

    @staticmethod
    def _kaiju_workflow(kwargs, steps):
        """
        Runs Kaiju workflow
        :return:
        """
        _ = steps
        KaijuWorkflow.main(**kwargs)

    def parse_options(self, options):
        """
        Parses options and returns correct workflow.
        :type options: argparse.Namespace
        :param options: arguments passed by the parser.
        :return: Runs the specified subparser in options.subparser_name.
        """
        subparsers = {
            "genome_annotation": lambda _options, _steps: self._genome_annotation(
                _options, _steps
            ),
            "blastn": lambda _options, _steps: self._blastn_alignment(_options, _steps),
            "kaiju": lambda _options, _steps: self._kaiju_workflow(_options, _steps),
        }

        # Run desired subparser
        kwargs = dict(options._get_kwargs())
        steps = kwargs.pop("steps")
        subparsers[options.subparser_name](kwargs, steps)
