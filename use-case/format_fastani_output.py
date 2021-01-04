#!/usr/bin/env python
# coding: utf-8


import argparse
import pandas as pd
from pathlib import Path


def main(input_file, output_file=None, invert=False):
    df = pd.read_csv(input_file, sep="\t")

    if invert:
        df = abs(df - 100)

    for i in df.index:
        for j in df.columns:
            if i == j:
                if invert:
                    df.loc[i, j] = 0
                else:
                    df.loc[i, j] = 100

    if output_file is None:
        output_file = input_file.replace(Path(input_file.stem), "_format.txt")

    df.to_csv(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Formats a fastANI output file into a symmetric table."
    )
    parser.add_argument("-i", "--input", help="File created by fastANI.", required=True)
    parser.add_argument("-o", "--output", help="Output symmetric table.", required=True)
    parser.add_argument(
        "--invert",
        help="Invert ANI values (returns |ANI - 100|), useful for hierarchical clustering.",
        action="store_true",
        required=False,
    )

    args = parser.parse_args()

    main(args.input_file, args.output_file, args.invert)
