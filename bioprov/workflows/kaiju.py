#!/usr/bin/env python
__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Kaiju workflow module

'Run Kaiju on metagenomic data and create reports for taxonomic ranks.'

This can be run by itself as a script or called
with the BioProv CLI application (recommended).
"""

from os import path, getcwd, mkdir
from bioprov import config, from_df
from bioprov.programs import kaiju, kaiju2table
from bioprov.utils import Warnings, tax_ranks
from tqdm import tqdm
import argparse
import pandas as pd


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

        print(Warnings()["sample_loading"](len(df)))

        # Create BioProv Project
        ss = from_df(df, index_col="sample-id", file_cols=("R1", "R2"), tag=_tag)

        success, skip = 0, 0

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
                k2t_run = kaiju2table_.run(sample, _print=False)

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


if __name__ == "__main__":
    parser = KaijuWorkflow.parser()
    args = parser.parse_args()
    if args.output_directory is None:
        args.output_directory = getcwd()

    if not path.isdir(args.output_directory):
        mkdir(args.output_directory)

    KaijuWorkflow.main(
        input_file=args.input,
        output_path=args.output_directory,
        kaijudb=args.kaiju_db,
        nodes=args.nodes,
        names=args.names,
        threads=args.threads,
        _tag=args.tag,
        verbose=args.verbose,
        kaiju_params=args.kaiju_params,
        kaiju2table_params=args.kaiju2table_params,
    )
