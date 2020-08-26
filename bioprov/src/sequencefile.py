__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Contains the SequenceFile class and related functions.
"""

from bioprov.src.file import File
from Bio import SeqIO
from collections import namedtuple
from statistics import mean, median
from pathlib import Path
from bioprov.utils import warnings


class SequenceFile(File):
    """
    Class for holding sequence file and sequence information. Inherits from File.
    """

    def __init__(
        self, path, tag=None, import_data=False, _format="fasta",
    ):
        """
        :param path: A UNIX-like file path.
        :param tag: optional tag describing the file.
        :param import_data: Whether to import sequence data as Bio.SeqRecord.SeqRecord
        :param _format: Input format. Only 'fasta' is supported for now.
        """
        File.__init__(self, path, tag)
        if not self.exists:
            import_data = False
        if import_data:
            self.import_data(_format=_format)
        else:
            self.records, self.seqstats = (None, None)

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
        self.import_data()
        return self._records

    @records.setter
    def records(self, value):
        self._records = value

    @property
    def seqstats(self):
        return seqstats(self.path)

    @seqstats.setter
    def seqstats(self, value):
        self._seqstats = value

    def import_data(self, _format="fasta"):
        if self.exists:
            self.records = SeqIO.to_dict(seqrecordgenerator(self.path, _format))
            self.seqstats = seqstats(self.path)
        else:
            self.records, self.seqstats = (None, None)

    pass


def seqrecordgenerator(path, _format="fasta"):
    """
    :param path: Path to a valid FASTA file.
    :param _format: format to pass to SeqIO.parse(). Only fasta is supported.
    :return: A generator of SeqRecords.
    """
    try:
        records = SeqIO.parse(path, format=_format)
        return records
    except FileNotFoundError as e:
        print(e)
        return None


def seqstats(path, megabases=False, percentage=False, calculate_gc=True, decimals=5):
    """
    Get sequence statistics from a FASTA file.
    Inspired from the program Seqstats

    :param path: A valid FASTA file.
    :param megabases: If true, express number of base pairs in megabases.
    :param decimals: Number of decimals in GC content.
    :param percentage: Express GC content in percentage instead of fraction.
    :param calculate_gc: Whether to calculate GC. Disabled if sequence is aminoacid.
    :return: Number of base pairs,
    """
    if not Path(path).exists:
        warnings["not_exist"](path)
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

    aminoacids = "LMFWKQESPVIYHRND"

    # Calculate statistics
    for ix, SeqRecord in enumerate(sequences):
        if ix == 1:
            seq = str(SeqRecord.seq)
            if any(i in aminoacids for i in seq):
                calculate_gc = False
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
    if calculate_gc:
        gc = round(gc / total_bps, decimals)
        if percentage:
            gc *= 100
    else:
        gc = "NA"

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
