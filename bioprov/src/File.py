"""
Contains the File class and related functions.
"""
from pathlib import Path
from .utils import get_size


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
        return str(self.path)

    def __str__(self):
        return self.__repr__()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def exists(self):
        return self.path.exists()

    @exists.setter
    def exists(self, _):
        self._exists = self.path.exists()

    pass
