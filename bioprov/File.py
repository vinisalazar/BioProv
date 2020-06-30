"""
Contains the File class and related functions.
"""
from pathlib import Path


class File:
    """
    Class for holding file and file information.
    """

    def __init__(self, path, tag=None, generated_by=None):
        """
        :param path: A UNIX-like file path.
        :param tag: optional tag describing the file.
        :param generated_by: An instance of the Run class which generated the command.
        """
        self.path = Path(path).absolute()
        self.name = self.path.stem
        self.directory = self.path.parent
        self.extension = self.path.suffix
        if tag is None:
            tag = self.name
        self.tag = tag
        self.exists = self.path.exists()
        self.size = get_size(self.path)
        self.raw_size = get_size(self.path, convert=False)
        self.generated_by = generated_by

    def __repr__(self):
        if self.exists is True:
            return f"File {self.name} with {self.size} in directory {self.directory}."
        else:
            return (
                f"Path {self.name} in directory {self.directory}. File does not exist."
            )

    def __str__(self):
        return str(self.path)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def exists(self):
        return self._exists

    @exists.setter
    def exists(self, value):
        self._exists = value

    pass


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
