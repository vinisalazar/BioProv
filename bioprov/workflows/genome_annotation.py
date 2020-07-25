#!/usr/bin/env python

"""
Genome annotation workflow module.

'Genome annotation with Prodigal, Prokka and the COG database.'

This can be run by itself as a script or called
with the BioProv CLI application (recommended).
"""

import argparse
import sys
from os import path, listdir
import pandas as pd
from bioprov import from_df, config
from bioprov.utils import warnings
from bioprov.programs import prodigal, prokka
from tqdm import tqdm


class GenomeAnnotation:
    """
    Class holding the GenomeAnnotation main function and parser.
    """

    description = "Genome annotation with Prodigal, Prokka and the COG database."

    def __init__(self):
        pass

    @staticmethod
    def main(
        _input_path,
        labels,
        files,
        _tag,
        run_prokka,
        _skip_prodigal,
        _verbose,
        _threads,
        _directory_input=False,
    ):
        """
        Main function to run the GenomeAnnotation workflow.

        :param _input_path: A tab delimited file where assembly files are the first column
        :param labels: Name of the column containing the labels.
        :param files: Name of the column containing the files.
        :param _tag: Tag to name the dataframe.
        :param run_prokka: Whether to run Prokka or not.
        :param _skip_prodigal: Whether to skip running Prodigal or not.
        :param _verbose: More verbose output.
        :param _threads: Number of threads.
        :param _directory_input: Provide a directory instead of file as input (default is False)
        :return:
        """
        if _directory_input:
            dataframe = pd.DataFrame(listdir(_input_path))
        else:
            dataframe = pd.read_csv(_input_path, sep="\t")

        # Read input and initial error checking.
        dataframe.columns = (files, *dataframe.columns[1:])
        dataframe[files] = dataframe[files].apply(lambda s: path.abspath(s))
        for file in dataframe[files]:
            assert path.isfile(file), warnings["not_exist"](file)

        print(warnings["sample_loading"](len(dataframe)))

        # Parse labels
        if labels is not None:
            assert labels in dataframe.columns
            dataframe["label"] = dataframe[labels]
        else:  # Get automatically from filenames.
            dataframe["label"] = dataframe[files].apply(
                lambda s: path.splitext(path.basename(s))[0]
            )

        # Create BioProv SampleSet
        ss = from_df(dataframe, index_col="label", sequencefile_cols=files)
        for k, sample in ss.items():
            sample.files["assembly"] = sample.files.pop(
                files
            )  # rename whatever the files column was called.
        ss.tag = _tag

        success = 0

        for k, sample in tqdm(ss.items()):

            # Prodigal block
            prodigal_ = prodigal(sample)
            if not _skip_prodigal:
                prodigal_run = prodigal_.run(sample)
                if _verbose:
                    print(prodigal_run)

            # Prokka block
            if run_prokka:
                prokka_ = prokka(sample, threads=_threads)
                prokka_run_ = prokka_.run(sample)
                if _verbose:
                    print(prokka_run_)
            if all(file_.exists for _, file_ in sample.files.items()):
                success += 1

        print(warnings["number_success"](success, len(dataframe)))

        ss.to_json()

    @classmethod
    def parser(cls):
        """
        Parser for the GenomeAnnotation workflow.
        :return: instance of argparse.ArgumentParser.
        """
        _parser = argparse.ArgumentParser(
            "genome_annotation", description=GenomeAnnotation.description,
        )
        _parser.add_argument(
            "-i",
            "--input",
            help=(
                "Input, may be a tab-delimited file where the first column is the path to"
                " each assembly,or a directory (if the -d option is on)."
            ),
            required=True,
            type=str,
        )
        _parser.add_argument(
            "-f",
            "--files",
            help=(
                "Column in input file containing paths to each assembly file. Default is"
                " 'assembly'."
            ),
            default="assembly",
        )
        _parser.add_argument(
            "-l",
            "--labels",
            help=(
                "Column in input file to assign labels. If input is a directory, will get"
                " automatically."
            ),
            required=False,
            type=str,
        )
        _parser.add_argument(
            "-d",
            "--directory",
            help="Provide a directory instead of a file as input.",
            required=False,
            default=False,
            action="store_true",
        )
        _parser.add_argument(
            "--run_prokka",
            help="Whether to run Prokka.",
            default=False,
            required=False,
            action="store_true",
        )
        _parser.add_argument(
            "--skip_prodigal",
            help="Whether to skip running Prodigal.",
            default=False,
            required=False,
            action="store_true",
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
    parser = GenomeAnnotation.parser()
    args = parser.parse_args()
    (
        input_path,
        labels_column,
        directory_input,
        file_column,
        tag,
        prokka_run,
        skip_prodigal,
        verbose,
        threads,
    ) = (
        args.input,
        args.labels,
        args.directory,
        args.files,
        args.tag,
        args.run_prokka,
        args.skip_prodigal,
        args.verbose,
        args.threads,
    )
    if not path.exists(input_path):
        parser.print_help()
        print(f"Input path '{input_path}' does not exist!")
        sys.exit(0)
    GenomeAnnotation.main(
        input_path,
        labels_column,
        file_column,
        tag,
        prokka,
        skip_prodigal,
        verbose,
        threads,
        directory_input,
    )
