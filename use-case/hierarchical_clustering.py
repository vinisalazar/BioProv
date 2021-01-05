#!/usr/bin/env python
# coding: utf-8

import argparse
import pandas as pd
from glob import glob
from os import path, listdir, mkdir
from matplotlib import rc
from matplotlib import pyplot as plt
from scipy.spatial.distance import squareform, pdist
from scipy.cluster.hierarchy import dendrogram, linkage
from PIL import Image


def main(table, labels, output_file, color_thresold, rotate):
    Z, columns = hclust(table, labels)
    plot_hclust(
        Z, columns, save=output_file, color_thresold=color_thresold, rotate=rotate
    )
    if path.isfile(output_file):
        print(f"Created dendrogram as {output_file}.")


def hclust(table, labels=None):
    """
    table: comma-separated dataframe containing a symmetrical table.
    labels: comma-separated dataframe with the first column as the old name and second as the new name.
    """
    table = pd.read_csv(table)
    if labels:
        labels = pd.read_csv(labels)
        labels.columns = "old", "new"
        renaming_dict = pd.Series(labels["new"].values, index=labels["old"]).to_dict()
        table.rename(columns=renaming_dict, index=renaming_dict, inplace=True)

    X = abs(table - 99.99)
    X = squareform(X)
    Z = linkage(X, method="complete", metric="cityblock", optimal_ordering=True)

    return (Z, table.columns)


def augmented_dendrogram(*args, **kwargs):

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get("no_plot", False):
        for i, d in zip(ddata["icoord"], ddata["dcoord"]):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > 1.5:
                plt.plot(x, y, "ro")
                plt.annotate(
                    "%.3g" % y,
                    (x, y),
                    xytext=(0, -8),
                    textcoords="offset points",
                    va="top",
                    ha="center",
                )

    return ddata


def plot_hclust(Z, columns, figsize=False, save=False, rotate=True, color_threshold=30):
    if figsize:
        fig = plt.figure(figsize=figsize)

    dn = augmented_dendrogram(
        Z,
        labels=columns,
        leaf_rotation=-90,
        color_threshold=color_threshold,
        leaf_font_size=9,
    )

    if save:
        plt.savefig(save, dpi=1200, bbox_inches="tight")
    else:
        rotate = False

    if rotate:
        im = Image.open(save)
        im = im.rotate(90, expand=True)
        im.save(save)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a hierarchical clustering with the Manhattan distance and plots a dendrogram of the given distance table."
    )
    parser.add_argument(
        "-t",
        "--table",
        help="Comma-separated file containing symmetrical table.",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--labels",
        help="Used to rename the rows and columns of the input table. Must be comma-separated with two columns, the old name and the new (no header).",
    )
    parser.add_argument(
        "-o", "--output_file", help="Name of the output_file.", default=None
    )
    parser.add_argument(
        "-c",
        "--color_thresold",
        help="Color threshold of the dendrogram. Default is 30.",
        type=int,
        default=30,
    )
    parser.add_argument(
        "-r", "--rotate", help="Whether to rotate the dendrogram.", action="store_true"
    )

    args = parser.parse_args()

    if args.output_file is None:
        args.output_file = "dendrogram.pdf"

    main(args.table, args.labels, args.output_file, args.color_threshold, args.rotate)
