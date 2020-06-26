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
        File.__init__(self, path, tag)
        self.records = seqrecordgenerator(self.path)

    pass


def seqrecordgenerator(path):
    """
    :param path: Path to a valid FASTA file.
    :return: A SeqIO SeqRecords generator.
    """
    return SeqIO.parse(path, format="fasta")
