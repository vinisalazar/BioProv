"""
Testing module for the package
"""


def test_import_bioprov():
    try:
        import bioprov as bp
    except ImportError:
        raise


def test_import_classes():
    try:
        from bioprov import Config, File, SequenceFile
    except ImportError:
        raise
