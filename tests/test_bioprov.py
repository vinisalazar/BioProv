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
            src,
            cli,
            data,
        )
    except ImportError:
        raise


def test_import_packages():
    """
    Test if supplementary packages can be imported correctly
    :return: ImportError if not able to import
    """
    try:
        from bioprov.data import data_dir, genomes_dir, synechococcus_genome
        from bioprov.cli import CLI
        from bioprov.programs import prodigal
    except ImportError:
        raise
