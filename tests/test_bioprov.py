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


def test_import_classes():
    """
    Test if all classes can be imported correctly.
    :return: ImportError if not able to import
    """
    try:
        from bioprov import (
            Config,
            File,
            Program,
            Parameter,
            Run,
            SequenceFile,
            cli,
            data,
        )
    except ImportError:
        raise


def test_import_data():
    """
    Test if data can be imported correctly
    :return: ImportError if not able to import
    """
    try:
        from bioprov.data import data_dir, genomes_dir, synechococcus_genome
        from bioprov.cli import CLI
    except ImportError:
        raise
