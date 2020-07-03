"""
Contains the SequenceFile class and related functions.
"""

from bioprov import File
from Bio import SeqIO
from collections import namedtuple
from statistics import mean, median
from pathlib import Path


class SequenceFile(File):
    """
    Class for holding sequence file and sequence information. Inherits from File.
    """

    def __init__(self, path, tag=None, import_data=True):
        """
        :param path: A UNIX-like file path.
        :param tag: optional tag describing the file.
        """
        File.__init__(self, path, tag)
        if not self.exists:
            import_data = False
        if import_data:
            self.records = seqrecordgenerator(self.path)
            self.seqstats = seqstats(self.path)
        else:
            self.records, self.seqstats = False, False

    def __len__(self):
        return self.seqstats.total_bps

    def __getitem__(self, key):
        try:
            return self.records[key]
        except KeyError:
            print(f"{key} does not exist. Please check the existing keys.")
            raise

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, value):
        try:
            self._records = SeqIO.to_dict(value)
        except TypeError:  # in case the file does not exist
            not_exist(self.path)
            self._records = False

    @property
    def seqstats(self):
        return self._seqstats

    @seqstats.setter
    def seqstats(self, value):
        self._seqstats = value

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
        return False


def seqstats(path, megabases=False, percentage=False, decimals=5):
    """
    Get sequence statistics from a FASTA file.
    Inspired from the program Seqstats

    :param path: A valid FASTA file.
    :param megabases: If true, express number of base pairs in megabases.
    :param decimals: Number of decimals in GC content.
    :param percentage: Express GC content in percentage instead of fraction.
    :return: Number of base pairs,
    """
    if not Path(path).exists:
        not_exist(path)
        return False

    sequences = seqrecordgenerator(path)
    Seqstats = namedtuple(
        "Seqstats",
        (
            "number_seqs",
            "total_bps",
            "gc",
            "avg_bp",
            "median_bp",
            "n50",
            "min_bp",
            "max_bp",
        ),
    )

    seq_bps, gc = [], 0

    # Calculate statistics
    for SeqRecord in sequences:
        seq_bps.append(len(SeqRecord.seq))
        gc += SeqRecord.seq.upper().count("G")
        gc += SeqRecord.seq.upper().count("C")

    number_seqs = len(seq_bps)
    total_bps = sum(seq_bps)
    avg_bp = round(mean(seq_bps), decimals)
    median_bp = median(seq_bps)
    n50 = calculate_n50(seq_bps)
    min_bp = min(seq_bps)
    max_bp = max(seq_bps)

    # Calculate GC content
    gc = round(gc / total_bps, decimals)
    if percentage:
        gc *= 100

    if megabases:
        total_bps /= 10e5

    return Seqstats(number_seqs, total_bps, gc, avg_bp, median_bp, n50, min_bp, max_bp)


def calculate_n50(numlist):
    """
    Calculate N50 from a list of contig lengths.
    https://github.com/vikas0633/python/blob/master/N50.py

    Based on the Broad Institute definition:
    https://www.broad.harvard.edu/crd/wiki/index.php/N50
    :param numlist: list of contig lengths
    :return: N50 value
    """
    numlist.sort()
    newlist = []
    for x in numlist:
        newlist += [x] * x
    # take the mean of the two middle elements if there are an even number
    # of elements.  otherwise, take the middle element
    if len(newlist) % 2 == 0:
        medianpos = int(len(newlist) / 2)
        return newlist[medianpos] + newlist[medianpos - 1] / 2
    else:
        medianpos = int((len(newlist) / 2) - 0.5)
        # noinspection PyTypeChecker
        return newlist[medianpos]


def not_exist(x):  # To-do: refactor this, maybe as static method?
    print(f"File {x} does not exist!")
    return
