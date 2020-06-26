"""
Files module containing classes File and SequenceFile.
"""
from pathlib import Path


class File:
    """
    Class for holding file and file information.
    """

    def __init__(self, path, tag=None):
        """
        :param path: A UNIX-like file path.
        :param tag: optional tag describing the file.
        """
        self.path = Path(path).absolute()
        self.name = self.path.stem
        self.directory = self.path.parent
        self.extension = self.path.suffix
        self.tag = tag
        self.exists = self.path.exists()
        self.size = get_size(self.path)
        self.raw_size = get_size(self.path, convert=False)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    pass


class SequenceFile(File):
    """
    Class for holding sequence file and sequence information. Inherits from File.
    """

    pass


def convert_bytes(num):
    """
    Helper function to convert bytes into KB, MB, etc.

    From https://stackoverflow.com/questions/2104080/how-can-i-check-file-size-in-python
    """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def get_size(path, convert=True):
    """
    Calculate size of a given file.
    :param path: Valid path of a file.
    :param convert: Whether to convert the values to bytes, KB, etc.
    :return: Size with converted values. 0 if file does not exist.
    """
    path = Path(path)
    size = path.stat().st_size
    if path.exists:
        if convert:
            return convert_bytes(size)
        else:
            return size
    else:
        return 0
