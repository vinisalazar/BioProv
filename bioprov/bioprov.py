__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.2"

"""
BioProv command-line application. This module holds the main executable.
"""

import argparse
import sys
from bioprov.workflows import WorkflowOptionsParser, genome_annotation, KaijuWorkflow
from bioprov.utils import parser_help


def main():
    bioprov_parser = argparse.ArgumentParser(
        description="BioProv command-line application. Choose a workflow to begin.",
    )
    subparsers = bioprov_parser.add_subparsers(title="workflows", dest="subparser_name")
    _ = subparsers.add_parser("genome_annotation")
    _ = subparsers.add_parser("kaiju")
    subparsers.choices["genome_annotation"] = genome_annotation().parser
    subparsers.choices["kaiju"] = KaijuWorkflow.parser()

    # Refactoring to subparsers
    args = None
    if len(sys.argv) == 1 or sys.argv[1] == "-h" or sys.argv == "--help":
        parser_help(bioprov_parser)
    else:
        args = bioprov_parser.parse_args()

    parser = WorkflowOptionsParser()
    parser.parse_options(args)


if __name__ == "__main__":
    main()
