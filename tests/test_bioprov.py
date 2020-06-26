"""
Testing module for the package BioProv.

Tests include:
    - Imports;
    - Class generation and methods.
"""
import random
import string
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
        from bioprov import Config, File, SequenceFile, get_size
    except ImportError:
        raise


def test_File():
    """
    Tests objects in the File module:
        - existing File
        - non-existing File
        - get_size(), convert_bytes()
    :return:
    """
    import bioprov as bp

    # Test existing file
    file, tag = bp.__file__, "Init file for BioProv."
    f = bp.File(file, tag)
    non_existing = randomString() + "." + randomString(3)
    nf = bp.File("./" + non_existing)
    attributes = {
        # File class - existing file
        "path": f.path == Path(file).absolute(),
        "name": f.name == f.path.stem,
        "dir": f.directory == f.path.parent,
        "extension": f.extension == f.path.suffix,
        "tag": f.tag == tag,
        "exists": f.exists is True,
        "get_size": f.size == bp.get_size(f.path),  # get_size() function
        "raw_get_size": f.raw_size
        == bp.get_size(f.path, convert=False),  # get_size(convert=False)
        "non_existing": nf.exists is False,
        "no_size": nf.size is 0,
        "convert_bytes": bp.convert_bytes(2 ** 10) == "1.0 KB",
    }
    for k, statement in attributes.items():
        assert statement, f"{k} did not pass!"


def randomString(n=8):
    """
    Generate random strings for testings
    :param n: Length of string.
    :return: Random string of n characters.
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(n))
