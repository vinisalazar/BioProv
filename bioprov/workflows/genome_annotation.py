#!/usr/bin/env python
"""
Workflow for assembly evaluation and genome annotation.

1. Run Prodigal
2. Run Prokka
3. COG annotation
"""

import argparse
import sys
from os import path, listdir
import pandas as pd
import bioprov as bp
from bioprov.programs import prodigal


def main(dataframe, labels, files, _tag):
    """
    :param dataframe: A tab delimited file where assembly files are the first column
    :param labels: Name of the column containing the labels.
    :param files: Name of the column containing the files.
    :param _tag: Tag to name the dataframe.
    :return:
    """
    # Read input and initial error checking.
    dataframe.columns = (files, *df.columns[1:])
    dataframe[files] = dataframe[files].apply(lambda s: path.abspath(s))
    for file in dataframe[files]:
        assert path.isfile(
            file
        ), f"{file} was not found! Please check the correct path."
    print(f"Loading {len(dataframe)} samples.")

    # Parse labels
    if labels is not None:
        assert labels in df.columns
        dataframe["label"] = dataframe[labels]
    else:  # Get automatically from filenames.
        dataframe["label"] = dataframe[files].apply(
            lambda s: path.splitext(path.basename(s))[0]
        )

    ss = bp.from_df(dataframe, index_col="label", sequencefile_cols=files)
    for k, sample in ss.items():
        sample.files["assembly"] = sample.files.pop(
            files
        )  # rename whatever the files column was called.
    ss.tag = _tag

    ix, success = 1, 0

    for k, sample in ss.items():
        print(f"Processing sample {ix}/{len(dataframe)}.")
        p = prodigal(sample)
        _run = p.run(sample)
        if all(file_.exists for _, file_ in sample.files.items()):
            success += 1
        ix += 1

    ss.to_json()
    print(f"Ran successfully for {success}/{len(dataframe)} samples.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="genome annotation",
        description="Genome annotation with Prodigal, Prokka and the COG database.",
    )
    parser.add_argument(
        "-i",
        "--input",
        help=(
            "Input, may be a tab-delimited file where the first column is the path to"
            " each assembly,or a directory (if the -d option is on)."
        ),
        required=True,
        type=str,
    )
    parser.add_argument(
        "-f",
        "--files",
        help=(
            "Column in input file containing paths to each assembly file. Default is"
            " 'assembly'."
        ),
        default="assembly",
    )
    parser.add_argument(
        "-l",
        "--labels",
        help=(
            "Column in input file to assign labels. If input is a directory, will get"
            " automatically."
        ),
        required=False,
        type=str,
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="Provide a directory instead of a file as input.",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument("-t", "--tag", help="A tag for the dataset", required=False)
    args = parser.parse_args()
    input_path, labels_column, directory_input, file_column, tag = (
        args.input,
        args.labels,
        args.directory,
        args.files,
        args.tag,
    )
    if not path.exists(input_path):
        parser.print_help()
        print(f"Input path '{input_path}' does not exist!")
        sys.exit(0)
    if directory_input:
        df = pd.DataFrame(listdir(input_path))
    else:
        df = pd.read_csv(input_path, sep="\t")
    main(df, labels_column, file_column, tag)
