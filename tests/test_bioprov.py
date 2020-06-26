"""
Testing module for the package BioProv.

Tests include:
    - Imports;
    - Class generation and methods.
"""
from pathlib import Path


def test_import_bioprov():
    """
    Test if the package can be imported correctly.
    :return: ImportError if not able to import.
    """
    try:
        import bioprov as bp
    except ImportError:
        raise


def test_import_classes():
    """
    Test if all classes can be imported correctly.
    :return: ImportError if not able to import
    """
    try:
        from bioprov import Config, File, SequenceFile
    except ImportError:
        raise


def test_File():
    """
    Test if the File class works as expected.
    :return:
    """
    import bioprov as bp

    file, tag = bp.__file__, "Init file for BioProv."
    f = bp.File(file, tag)
    attributes = {
        "path": f.path == Path(file).absolute(),
        "name": f.name == f.path.stem,
        "dir": f.directory == f.path.parent,
        "extension": f.extension == f.path.suffix,
        "tag": f.tag == tag,
        "exists": f.exists,
        "size": float(f.size.split()[0]),  # Convert string to float
        "raw_size": f.raw_size,  # See if larger than 0
    }
    for k, statement in attributes.items():
        assert statement, f"{k} did not pass!"
