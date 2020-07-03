"""
Testing for the File module.
"""
import bioprov as bp
from pathlib import Path


def test_File():
    """
    Tests objects in the File module:
        - existing File instance
        - non-existing File instance
        - get_size(), convert_bytes()
    :return:
    """

    # Test existing file
    file, tag = bp.__file__, "Init file for BioProv."
    f = bp.File(file, tag)
    non_existing = bp.random_string() + "." + bp.random_string(3)
    nf = bp.File("./" + non_existing)
    attributes = {
        # File class - existing file
        "path": f.path == Path(file).absolute(),
        "name": f.name == f.path.stem,
        "dir": f.directory == f.path.parent,
        "extension": f.extension == f.path.suffix,
        "tag": f.tag == tag,
        "exists": f.exists is True,
        "repr": f.__repr__() == str(f.path),
        # Non existing file
        "non_existing": nf.exists is False,
        "no_size": nf.size is 0,
        "nf_repr": nf.__repr__() == str(nf.path),
        # get_size() function
        "get_size": f.size == bp.get_size(f.path),
        "raw_get_size": f.raw_size
        == bp.get_size(f.path, convert=False),  # get_size(convert=False)
        # Convert bytes function
        "convert_bytes": bp.convert_bytes(2 ** 10) == "1.0 KB",
    }
    for k, statement in attributes.items():
        assert statement, f"{k} did not pass!"
