__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.1"


"""
Contains the File class and related functions.
"""
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from Bio import SeqIO
from bioprov.utils import get_size
from prov.model import ProvEntity


class File:
    """
    Class for holding file and file information.
    """

    def __init__(self, path, tag=None, document=None, attributes=None):
        """
        :param path: A UNIX-like file path.
        :param tag: optional tag describing the file.
        :param document: prov.model.ProvDocument
        :param attributes: Miscellaneous attributes.
        """
        self.path = Path(path).absolute()
        self.name = self.path.stem
        self.basename = self.path.name
        self.directory = self.path.parent
        self.extension = self.path.suffix
        if tag is None:
            tag = self.name
        if attributes is None:
            attributes = {}
        self.tag = tag
        self.attributes = attributes
        self._exists = self.path.exists()
        self.size = get_size(self.path)
        self.raw_size = get_size(self.path, convert=False)

        # Provenance attributes
        self._document = document
        self._entity = ProvEntity(
            self._document, identifier="files:{}".format(self.basename)
        )

    def __repr__(self):
        return str(self.path)

    def __str__(self):
        return self.__repr__()

    @property
    def exists(self):
        return self.path.exists()

    @exists.setter
    def exists(self, value):
        self._exists = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, document):
        self._document = document

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, document):
        self._document = document
        self._entity = ProvEntity(self._document, self.path.name)


class SeqFile(File):
    """
    Class for holding sequence file and sequence information. Inherits from File.
    """

    def __init__(
        self, path, tag=None, document=None, import_records=True, format="fasta",
    ):
        """
        :param path: A UNIX-like file path.
        :param format: Format to be parsed by SeqIO.parse()
        :param tag: optional tag describing the file.
        :param import_records: Whether to import sequence data as Bio.SeqRecord.SeqRecord
        """
        super().__init__(path, tag, document)
        self.format = format
        self._generator = None
        self.records = None

        if self.exists:
            self.seqrecordgenerator()
        else:
            import_records = False

        if import_records:
            self.import_records()

    def seqrecordgenerator(self):
        """
        Runs seqrecordgenerator with the format.
        """
        self._generator = seqrecordgenerator(self.path, format=self.format)

    @property
    def generator(self):
        if self._generator is None:
            self.seqrecordgenerator()
        return self._generator

    @generator.setter
    def generator(self, value):
        self._generator = value

    def import_records(self):
        assert self.exists, "Cannot import, file does not exist."
        self.records = SeqIO.to_dict(self._generator)

    def calculate_stats(
        self, calculate_gc=True, megabases=False, percentage=False, decimals=5
    ):

        bp_array, GC = [], 0
        aminoacids = "LMFWKQESPVIYHRND"

        # We use enumerate to check the first item for amino acids.
        for ix, (key, seqrecord) in enumerate(self.records.items()):
            if ix == 0:
                seq = str(seqrecord.seq)
                if any(i in aminoacids for i in seq):
                    calculate_gc = False

            # Add length of sequences (number of base pairs)
            bp_array.append(len(seqrecord.seq))

            # Only count if there are no aminoacids.
            if calculate_gc:
                GC += seqrecord.upper().count("G")
                GC += seqrecord.upper().count("C")

        # Convert to array
        bp_array = np.array(bp_array)
        number_seqs = len(bp_array)
        total_bps = bp_array.sum()
        mean_bp = round(bp_array.mean(), decimals)
        N50 = calculate_N50(bp_array)
        min_bp = bp_array.min()
        max_bp = bp_array.max()

        if calculate_gc:
            GC = round(GC / total_bps, decimals)
            if percentage:
                GC *= 100
        else:
            GC = np.nan

        if megabases:
            total_bps /= 10e5

        return SeqStats(number_seqs, total_bps, mean_bp, min_bp, max_bp, N50, GC)


@dataclass
class SeqStats:
    """
    Dataclass to describe sequence statistics.
    """

    number_seqs: int
    total_bps: int
    mean_bp: float
    min_bp: int
    max_bp: int
    N50: int
    GC: float


def calculate_N50(array):
    """
    Calculate N50 from an array of contig lengths.
    https://github.com/vikas0633/python/blob/master/N50.py

    Based on the Broad Institute definition:
    https://www.broad.harvard.edu/crd/wiki/index.php/N50
    :param array: list of contig lengths
    :return: N50 value
    """
    array.sort()
    new_array = []
    for x in array:
        new_array += [x] * x

    if len(new_array) % 2 == 0:
        ix = int(len(new_array) / 2)
        return (new_array[ix] + new_array[ix - 1]) / 2
    else:
        ix = int((len(new_array) / 2) - 0.5)
        return new_array[ix]


def seqrecordgenerator(path, format):
    """
    :param path: Path to file.
    :param format: format to pass to SeqIO.parse().
    :return: A generator of SeqRecords.
    """
    try:
        records = SeqIO.parse(path, format=format)
        return records
    except FileNotFoundError:
        raise
