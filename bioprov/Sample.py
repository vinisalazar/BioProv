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

    def add_file(self, files):
        """
        Adds file(s) to self.files. Must be a dict or an instance or iterable of bioprov.File.
        :param file: bioprov.File instance or dict with key, value where value is the file path.
        :return: Updates self by adding the file to self.files
        """

        # If it is a dict, we convert to File instances
        if isinstance(files, dict):
            files = {k: File(v, tag=k) for k, v in files.items()}

        # If it is an iterable of File instances, transform to a dict
        elif isinstance(files, list):
            files = {file.name: file for file in files}

        # If it is a single item, also transform to dict
        elif isinstance(files, File):
            files = {files.name: files}

        # Here files must be a dictionary of File instances
        for k, v in files.items():
            if k in self.files.keys():
                print(f"Updating file {k} with value {v}.")
            self.files[k] = v
