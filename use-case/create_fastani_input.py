#!/usr/bin/env python
# coding: utf-8

import sys
from os import path


def main():
    try:
        script, output_file, *files = sys.argv
    except ValueError:
        print("Invalid arguments. Please provide each file separated by space.")
        sys.exit(1)

    with open(output_file, "w") as f:
        for file in files:
            f.write(file + "\n")

    if path.isfile(output_file):
        print(f"Created file at '{output_file}'.")


if __name__ == "__main__":
    main()
