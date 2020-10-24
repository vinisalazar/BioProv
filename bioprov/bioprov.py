__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"

"""
BioProv command-line application. This module holds the main executable.
"""

import argparse
import sys
import bioprov.src.config as bp_config_module
from bioprov.src.config import config
from bioprov.workflows import WorkflowOptionsParser, genome_annotation, KaijuWorkflow
from bioprov.utils import parser_help, dict_to_string


def main(args=None):
    """
    Main function to run the BioProv command-line application.
    Calls the subparsers defined in the Workflows module.

    :param args: args to call the function with. Usually is None and
                 args are automatically extracted from the command line.
                 Passing args is used for testing only.
    """
    bioprov_parser = argparse.ArgumentParser(
        description="BioProv command-line application. Choose a command to begin.\n"
    )
    bioprov_parser.add_argument(
        "--show_config", help="Show location of config file", action="store_true"
    )
    bioprov_parser.add_argument(
        "-v", "--version", help="Show BioProv version", action="store_true"
    )
    workflows = bioprov_parser.add_subparsers(title="workflows", dest="subparser_name")
    _ = workflows.add_parser("genome_annotation")
    _ = workflows.add_parser("kaiju")
    workflows.choices["genome_annotation"] = genome_annotation().parser
    workflows.choices["kaiju"] = KaijuWorkflow.parser()

    # Refactoring to subparsers
    if args is None:
        if len(sys.argv) == 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
            parser_help(bioprov_parser)
        else:
            args = bioprov_parser.parse_args()  # no cover

    if args.show_config:
        print(
            "This is the location of the config module.\n"
            "Edit it to alter your BioProv settings.\n\n",
            f"'{bp_config_module.__file__}'\n",
        )
        print("These are your configuration settings:")
        print(dict_to_string(config.__dict__))

        sys.exit(0)
    elif args.version:
        print(f"Local BioProv version is v{__version__}")
        sys.exit(0)

    parser = WorkflowOptionsParser()
    parser.parse_options(args)


if __name__ == "__main__":
    main()  # no cover
