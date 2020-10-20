__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.9"

"""
Helper functions.
"""
import sys
from pathlib import Path
from prov.model import Namespace, QualifiedName


def convert_bytes(num):
    """
    Helper function to convert bytes into KB, MB, etc.
    From https://stackoverflow.com/questions/2104080/how-can-i-check-file-size-in-python

    :param num: Number of bytes.
    """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def get_size(path, convert=True):
    """
    Calculate size of a given file.
    :param path: Valid _path of a file.
    :param convert: Whether to convert the values to bytes, KB, etc.
    :return: Size with converted values. 0 if file does not exist.
    """
    path = Path(path)
    if path.exists():
        size = path.stat().st_size
        if convert:
            return convert_bytes(size)
        else:
            return size
    else:
        return 0


def parser_help(parser):
    """
    Shows help if no arguments are passed for parser.
    :param parser: An instance of argparse.ArgumentParser
    :return:
    """
    parser.print_help()
    return sys.exit(0)


tax_ranks = "phylum class order family genus species".split()


def assert_tax_rank(tax_rank):
    """
    Tests if a string is a valid taxonomic rank.
    :param tax_rank: String to be evaluated.
    :return: True or False.
    """
    return tax_rank in tax_ranks


class Warnings:

    """
    Class to handle warnings.
    """

    _warnings = {
        "not_exist": lambda x: f"File '{x}' does not exist!",
        "sample_loading": lambda n: f"Loading {str(n)} samples.",
        "invalid_tax_rank": lambda tax_rank: f"Rank '{tax_rank}' not in ranks, choose from:\n{tax_ranks}",
        "choices": lambda x, choices, argument: f"Argument '{argument}' of value '{x}' is invalid, please select from: {choices}",
        "number_success": lambda success, total: f"Ran successfully for {str(success)}/{str(total)} samples.",
        "number_skip": lambda skip: f"Skipped {str(skip)} samples.",
        "incorrect_type": lambda x, type_: f"'{x}' is of type '{type(x)}'; it must be an instance of '{type_}'",
    }

    def __init__(self):
        pass

    @classmethod
    def __getitem__(cls, item):
        return cls._warnings[item]


def serializer(object_):
    """
    Helper function to serialize objects into JSON compatible dictionaries.
    :param object_: A BioProv class instance.
    :return: JSON compatible dictionary.
    """
    serial_out = dict()

    if isinstance(object_, dict):
        pass
    else:
        object_ = object_.__dict__.copy()

    for k, v in object_.items():
        # Checks for serializer method
        if has_serializer(v):
            serial_out[k] = v.serializer()

        elif isinstance(v, dict):
            serial_out[k] = serializer(v)

        elif is_serializable_type(v):
            serial_out[k] = v
        # If none of the previous conditions apply, convert to str
        else:
            serial_out[k] = str(v)

    return serial_out


def has_serializer(object_):
    _has_serializer = getattr(object_, "serializer", None)
    return callable(_has_serializer)


def is_serializable_type(type_):
    serializable_types = (float, int, str, bool, type(None))
    return isinstance(type_, serializable_types)


def build_prov_attributes(dictionary, namespace):
    """
    Inserting attributes into a Provenance object can be tricky. We need a NameSpace for said object,
    and attributes must be named correctly. This helper function builds a dictionary of attributes
    properly formatted to be inserted into a namespace.

    :param dictionary: dict with object attributes.
    :param namespace: instance of Namespace.
    :return: List of tuples (QualifiedName, value)
    """

    # Check arg types
    assert isinstance(namespace, Namespace), Warnings()["incorrect_type"](
        namespace, Namespace
    )
    assert isinstance(dictionary, dict), Warnings()["incorrect_type"](dictionary, dict)

    attributes = []
    for k, v in dictionary.items():
        if k == "namespace":
            continue
        else:
            if not is_serializable_type(v):
                v = str(v)
            q = QualifiedName(namespace, str(k))
            attributes.append((q, v))

    return attributes


def dict_to_string(dictionary):
    """
    Converts a dictionary to string for pretty printing
    :param dictionary: dict
    :return: str
    """
    assert isinstance(dictionary, dict), Warnings()["incorrect_type"](dictionary, dict)
    return "\n".join(" " + k + ": " + str(v) for k, v in dictionary.items())


def serializer_filter(_object, keys):
    """
    Filters keys from _object.__dict__ to make custom serializers.

    :param _object: A bioprov object
    :param keys: keys to be filtered.
    :return: dict
    """
    serial_out = _object.__dict__.copy()

    for key in keys:
        if key in serial_out.keys():
            del serial_out[key]

    return serializer(serial_out)
