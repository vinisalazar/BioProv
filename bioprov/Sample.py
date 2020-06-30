"""
Contains the Sample class and related functions.
"""

from bioprov import File


class Sample:
    """
    Class for holding sample information and related files and programs.
    """

    def __init__(self, name=None, tag=None, files=None, attributes=None):
        """
        :str name:  Sample name or ID.
            :str tag: optional tag describing the sample.
        :dict files: Dictionary of files associated with the sample.
        :dict attributes: Dictionary of any other attributes associated with the sample.
        """
        self.name = name
        if isinstance(files, dict):
            files_ = dict()
            for k, v in files.items():
                if isinstance(v, File):
                    files_[k] = v
                else:  # if it is not a File instance, create one.
                    files_[k] = File(name=k, path=v)
            files = files_
        self.tag = tag
        self.files = files
        self.attributes = attributes

    pass
