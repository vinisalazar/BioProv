#!/usr/bin/env python
# coding: utf-8


import argparse
import pandas as pd
from pathlib import Path


def main(input_file, output_file=None, invert=False):
    df = pd.read_csv(input_file, sep="\t")
    df.columns = "genome-a genome-b mean-aai nfrags total-frags".split()
    df["genome-a"] = df["genome-a"].str.split("/", expand=True).iloc[:, -1]
    df["genome-b"] = df["genome-b"].str.split("/", expand=True).iloc[:, -1]

    df = pd.pivot_table(
        data=df, index="genome-a", columns="genome-b", values="mean-aai"
    )

    if invert:
        df = abs(df - 100)

    for i, ix in enumerate(df.index):
        for j, col in enumerate(df.columns):
            if i == j:
                if invert:
                    df.iloc[i, j] = 0
                else:
                    df.iloc[i, j] = 100
            else:
                mean = round((df.iloc[i, j] + df.iloc[j, i]) / 2, 3)
                df.iloc[i, j] = mean
                df.iloc[j, i] = mean

    if output_file is None:
        output_file = input_file.replace(Path(input_file.stem), "_format.txt")

    df.to_csv(output_file)
    if Path(output_file).exists():
        print(f"Created symmetrical table at {output_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Formats a fastANI output file into a symmetric table."
    )
    parser.add_argument(
        "-i", "--input_file", help="File created by fastANI.", required=True
    )
    parser.add_argument(
        "-o", "--output_file", help="Output symmetric table.", default=None
    )
    parser.add_argument(
        "--invert",
        help="Invert ANI values (returns |ANI - 100|), useful for hierarchical clustering.",
        action="store_true",
        required=False,
    )

    args = parser.parse_args()

    main(args.input_file, args.output_file, args.invert)
