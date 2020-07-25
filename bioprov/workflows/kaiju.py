"""
Kaiju workflow module

'Run Kaiju on metagenomic data and create reports for taxonomic ranks.'

This can be run by itself as a script or called
with the BioProv CLI application (recommended).
"""

from os import path, getcwd
from bioprov import config, from_df
from bioprov.programs import kaiju, kaiju2table
from bioprov.utils import warnings, tax_ranks
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
        :param _tag: Tag for SampleSet.
        :param verbose: Verbose output.
        :param resume: Check for existing files and skip running Kaiju for them.
        :param kaiju_params: Parameter string to add to Kaiju command.
        :param kaiju2table_params: Parameter string to add to kaiju2table command.
        :return:
        """
        # Asserting files exist
        for file_ in (input_file, kaijudb, nodes, names):
            assert path.isfile(file_), warnings["not_exist"](file_)

        # Asserting columns are correct
        df = pd.read_csv(input_file, sep="\t")
        for column in ("sample-id", "R1", "R2"):
            assert column in df.columns, "Column '{}' not present in {}.".format(
                column, input_file
            )

        warnings("sample_loading")(len(df))

        # Create BioProv SampleSet
        ss = from_df(df, index_col="sample-id", file_cols=("R1", "R2"), tag=_tag)

        success, skip = 0, 0

        for k, sample in tqdm(ss.items()):
            kaiju_ = kaiju(
                sample,
                output_path=output_path,
                kaijudb=kaijudb,
                nodes=nodes,
                threads=threads,
                r1=str(sample.files["R1"]),
                r2=str(sample.files["R2"]),
                add_param_str=kaiju_params,
            )

            # If resume is 'on', will check for existing files and skip if needed.
            if resume and sample.files["kaiju_output"].exists:
                skip += 1
                continue

            kaiju_run = kaiju_.run(sample)
            if verbose:
                print(kaiju_run)

            # Create reports for each rank (this is much faster than running Kaiju)
            for rank in tax_ranks:
                kaiju2table_ = kaiju2table(
                    sample,
                    output_path,
                    rank,
                    nodes,
                    names,
                    add_param_str=kaiju2table_params,
                )
                k2t_run = kaiju2table_.run(sample)
                if verbose:
                    print(k2t_run)

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
        warnings["number_success"](success, len(df))
        warnings["number_skip"](skip)

    @classmethod
    def parser(cls):
        """
        Parser for the Kaiju workflow.
        :return: instance of argparse.ArgumentParser.
        """
        _parser = argparse.ArgumentParser(
            "kaiju", description=KaijuWorkflow.description,
        )
        _parser.add_argument(
            "-i",
            "--input",
            help=(
                "Input file, a tab delimited file which must contain three columns: 'sample-id', 'R1', and 'R2',\
                containing respectively sample IDs, path to forward reads and path to reverse reads."
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
            "-db", "--kaiju_db", help="Kaiju database file.", required=True,
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
