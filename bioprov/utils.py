__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.2"

"""
Helper functions.
"""
import sys
from pathlib import Path


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
        "not_exist": lambda x: "File '{}' does not exist!".format(x),
        "sample_loading": lambda n: "Loading {} samples.".format(str(n)),
        "invalid_tax_rank": lambda tax_rank: "Rank '{}' not in ranks, choose from:\n{}".format(
            tax_rank, tax_ranks
        ),
        "choices": lambda x, choices, argument: "Argument '{}' of value '{}' is invalid, please select from: {}".format(
            argument, x, choices
        ),
        "number_success": lambda success, total: "Ran successfully for {}/{} samples.".format(
            str(success), str(total),
        ),
        "number_skip": lambda skip: "Skipped {} samples.".format(str(skip)),
        "incorrect_type": lambda x, type_: "'{}' is of type '{}'; it must be an instance of '{}'".format(
            x, type(x), type_
        ),
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
        object_ = object_.__dict__

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
