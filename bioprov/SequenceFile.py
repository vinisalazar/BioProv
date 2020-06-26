"""
Contains the SequenceFile class and related functions.
"""

from bioprov import File
from Bio import SeqIO


class SequenceFile(File):
    """
    Class for holding sequence file and sequence information. Inherits from File.
    """

    def __init__(self, path, tag=None):
        """
        :param path: A UNIX-like file path.
        :pram tag: optional tag describing the file.
        """
        File.__init__(self, path, tag)
        self.records = seqrecordgenerator(self.path)

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, value):
        try:
            self._records = SeqIO.to_dict(value)
        except TypeError:  # in case the file does not exist
            print(f"File {self.path} does not exist!")
            self._records = value

    pass


def seqrecordgenerator(path):
    """
    :param path: Path to a valid FASTA file.
    :return: A SeqIO SeqRecords generator.
    """
    try:
        records = SeqIO.parse(path, format="fasta")
        return records
    except FileNotFoundError as e:
        print(e)
        return None
