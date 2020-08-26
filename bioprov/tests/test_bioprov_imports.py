__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Testing module for the package BioProv.

Tests include:
    - Imports;
    - Class generation and methods.
"""


def test_import_bioprov():
    """
    Test if the package can be imported correctly.
    :return: ImportError if not able to import.
    """
    try:
        import bioprov
    except ImportError:
        raise


def test_import_classes_and_functions():
    """
    Test if all classes and functions can be imported correctly.
    :return: ImportError if not able to import
    """
    try:
        from bioprov import (
            Config,
            default_config,
            File,
            Program,
            Parameter,
            Run,
            Sample,
            Project,
            read_csv,
            from_df,
            from_json,
            SequenceFile,
        )
    except ImportError:
        raise


def test_import_packages():
    """
    Test if supplementary packages can be imported correctly.
    :return: ImportError if not able to import
    """
    try:
        from bioprov import src, data, programs, cli, workflows
        from bioprov.data import data_dir, genomes_dir, synechococcus_genome
        from bioprov.programs import prodigal, prokka, kaiju, kaiju2table
        from bioprov.cli import WorkflowOptionsParser
        from bioprov.workflows import KaijuWorkflow, genome_annotation
    except ImportError:
        raise
