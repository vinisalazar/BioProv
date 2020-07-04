"""
Helper functions.
"""
import random
import string
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


def random_string(n=8):
    """
    Generate random strings for tests.
    :param n: Length of string.
    :return: Random string of n characters.
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(n))


def get_size(path, convert=True):
    """
    Calculate size of a given file.
    :param path: Valid path of a file.
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
    if not len(sys.argv) > 1:
        parser.print_help()
        return sys.exit(0)
    else:
        return parser
