__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"

"""
BioProv command-line application. This module holds the main executable.
"""

import argparse
import sys
from pathlib import Path

import bioprov.src.config as bp_config_module
from bioprov.src.config import config
from bioprov.utils import parser_help, dict_to_string
from bioprov.workflows import (
    WorkflowOptionsParser,
    genome_annotation,
    blastn_alignment,
    KaijuWorkflow,
)


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

    # TODO: Make this into a subparser
    commands = bioprov_parser.add_mutually_exclusive_group()
    commands.add_argument(
        "--show_config", help="Show location of config file.", action="store_true"
    )
    commands.add_argument(
        "--show_provstore",
        help="Show location of ProvStore credentials file.",
        action="store_true",
    )
    commands.add_argument(
        "--create_provstore",
        help="Create ProvStore file credentials file.",
        action="store_true",
    )
    commands.add_argument(
        "--show_db", help="Show location of database file.", action="store_true"
    )
    commands.add_argument(
        "--clear_db", help="Clears all records in database.", action="store_true"
    )
    commands.add_argument(
        "-v", "--version", help="Show BioProv version", action="store_true"
    )
    commands.add_argument(
        "-l",
        "--list",
        help="List Projects in the BioProv database.",
        action="store_true",
    )
    workflows = bioprov_parser.add_subparsers(title="workflows", dest="subparser_name")
    _ = workflows.add_parser("genome_annotation")
    _ = workflows.add_parser("blastn")
    _ = workflows.add_parser("kaiju")
    workflows.choices["genome_annotation"] = genome_annotation().parser
    workflows.choices["blastn"] = blastn_alignment().parser
    workflows.choices["kaiju"] = KaijuWorkflow.parser()

    # Refactoring to subparsers
    if args is None:
        if len(sys.argv) == 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
            parser_help(bioprov_parser)
        else:
            args = bioprov_parser.parse_args()  # no cover

    for command, value in args.__dict__.items():
        if value:
            try:
                getattr(CommandOptionsParser, command)()
            except AttributeError:
                pass
    parser = WorkflowOptionsParser()  # no cover
    try:
        parser.parse_options(args)  # no cover
    except KeyError:
        raise


class CommandOptionsParser:
    def __init__(self):
        pass

    @classmethod
    def show_config(cls):
        print(
            "This is the location of the config module.\n"
            "Edit it to alter your BioProv settings.\n\n",
            f"'{bp_config_module.__file__}'\n",
        )
        print("These are your configuration settings:")
        print(dict_to_string(config.serializer()))

        sys.exit(0)

    @classmethod
    def show_provstore(cls):
        print(
            "This is the location of your ProvStore credentials file.\n"
            "Edit it to alter your BioProv settings.\n\n",
            f"{config.provstore_file}\n",
        )
        if not Path(config.provstore_file).is_file():
            print("It does not exist, but you can create one with the command:")
            print("  $ bioprov --create_provstore")

        sys.exit(0)

    @classmethod
    def create_provstore(cls):  # no cover
        config.create_provstore_file()
        sys.exit(0)

    @classmethod
    def show_db(cls):
        print(
            "This is the location of your BioProv database file.\n"
            f"'{config.db_path}'\n",
        )
        sys.exit(0)

    @classmethod
    def version(cls):
        print(f"Local BioProv version is v{__version__}")
        sys.exit(0)

    @classmethod
    def list(cls):
        tags = [f"'{project['tag']}'" for project in config.db.all()]
        print(f"You have {len(tags)} Projects in your database.")
        if tags:
            print("\n".join(tags))
        sys.exit(0)

    @classmethod
    def clear_db(cls):  # no cover
        config.db.clear_db()
        sys.exit(0)


if __name__ == "__main__":
    main()  # no cover
