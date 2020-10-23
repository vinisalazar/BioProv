__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Contains the File and SeqFile classes and related functions.
"""

import numpy as np
from dataclasses import dataclass
from pathlib import Path
from Bio import SeqIO, AlignIO
from bioprov.utils import (
    get_size,
    Warnings,
    serializer_filter,
    serializer,
    file_to_sha1,
    pattern_replacer,
)


class File:
    """
    Class for holding files and file information.
    """

    def __init__(self, path, tag=None, attributes=None, _get_hash=True):
        """
        :param path: A UNIX-like file _path.
        :param tag: optional tag describing the file.
        :param attributes: Miscellaneous attributes.
        """
        self.path = Path(path).absolute()
        assert (
            not self.path.is_dir()
        ), f"The path must be to a file, not a directory, you passed:\n'{path}'"
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
        self._sha1 = file_to_sha1(self.path)

        # Provenance attributes
        self._entity = None

    def __repr__(self):
        return str(self.path)

    def __str__(self):
        return self.__repr__()

    @property
    def sha1(self):
        return file_to_sha1(self.path)

    @sha1.setter
    def sha1(self, value):
        self._sha1 = value  # no cover

    @property
    def exists(self):
        return self.path.exists()

    @exists.setter
    def exists(self, value):
        self._exists = value  # no cover

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, value):
        self._entity = value

    def replace_path(self, old_terms, new, warnings=False):
        """
        Replace the current File path.

        Usually used for switching between users.

        :param old_terms: Terms to be replaced in the path.
        :param new: New term.
        :param warnings: Whether to warn if sha1 checksum differs or file does not exist.

        :return: Updates self.
        """
        old_hash, old_exists = self._sha1, self._exists
        self.path = Path(pattern_replacer(str(self.path), old_terms, new))
        # To-do: replace these print statements for logger warning/debug level
        if warnings:
            if not self.exists and old_exists:
                print(
                    f"Warning: file {self.path} was marked as existing but was not found."
                )
            if old_hash and self.sha1 != old_hash and self.exists:
                print(
                    f"Warning: file {self.path} previous sha1 checksum differs from the current."
                )

    def serializer(self):
        return serializer(self)


class SeqFile(File):
    """
    Class for holding sequence file and sequence information. Inherits from File.

    This class support records parsed with the BioPython.SeqIO module.
    """

    seqfile_formats = (
        "fasta",
        "clustal",
        "fastq",
        "fastq-sanger",
        "fastq-solexa",
        "fastq-illumina",
        "genbank",
        "gb",
        "nexus",
        "stockholm",
        "swiss",
        "tab",
        "qual",
    )

    def __init__(
        self,
        path,
        tag=None,
        format="fasta",
        parser="seq",
        document=None,
        import_records=False,
        calculate_seqstats=False,
    ):
        """
        :param path: A UNIX-like file _path.
        :param tag: optional tag describing the file.
        :param format: Format to be parsed by SeqIO.parse()
        :param parser: Bio parser to be used. Can be 'seq' (default) to be parsed by SeqIO or 'align'
                     to be parsed with AlignIO.
        :param document: prov.model.ProvDocument.
        :param import_records: Whether to import sequence data as Bio objects
        :param calculate_seqstats: Whether to calculate SeqStats
        """
        format_l = format.lower()
        assert format in SeqFile.seqfile_formats, Warnings()["choices"](
            format, "format", SeqFile.seqfile_formats
        )
        super().__init__(path, tag, document)
        self.format = format_l
        self.records = None
        self._generator = None
        self._seqstats = None
        self._parser = parser
        self.number_seqs: int
        self.total_bps: int
        self.mean_bp: float
        self.min_bp: int
        self.max_bp: int
        self.N50: int
        self.GC: float

        if self.exists:
            self._seqrecordgenerator()
        else:
            import_records = False
            calculate_seqstats = False

        if import_records:
            self.import_records()
            calculate_seqstats = True

        if calculate_seqstats:
            self._seqstats = self._calculate_seqstats(self.records)

    def _seqrecordgenerator(self):
        """
        Runs _seqrecordgenerator with the format.
        """
        self._generator = seqrecordgenerator(
            self.path, format=self.format, parser=self._parser
        )

    @property
    def generator(self):
        if self._generator is None:
            self._seqrecordgenerator()
        return self._generator

    @generator.setter
    def generator(self, value):
        self._generator = value

    @property
    def seqstats(self):
        if self._seqstats is None:
            self._seqstats = self._calculate_seqstats()
        return self._seqstats

    @seqstats.setter
    def seqstats(self, value):
        self._seqstats = value

    def import_records(self):
        assert self.exists, "Cannot import, file does not exist."
        self.records = SeqIO.to_dict(self._generator)

    def serializer(self):
        keys = ("records",)
        return serializer_filter(self, keys)

    def _calculate_seqstats(
        self,
        calculate_gc=True,
        megabases=False,
        percentage=False,
        decimals=5,
    ):
        """
        :param calculate_gc: Whether to calculate GC content. Disabled if amino acid file.
        :param megabases: Whether to convert number of sequences to megabases.
        :param percentage: Whether to convert GC content to percentage (value * 100)
        :param decimals: Number of decimals to round.
        :return: SeqStats instance.
        """
        assert isinstance(self.records, dict), Warnings()["incorrect_type"](
            self.records, dict
        )

        bp_array, GC = [], 0
        aminoacids = "LMFWKQESPVIYHRND"

        # We use enumerate to check the first item for amino acids.
        for ix, (key, SeqRecord) in enumerate(self.records.items()):
            if ix == 0:
                seq = str(SeqRecord.seq)
                if any(i in aminoacids for i in seq):
                    calculate_gc = False  # no cover

            # Add length of sequences (number of base pairs)
            bp_array.append(len(SeqRecord.seq))

            # Only count if there are no aminoacids.
            if calculate_gc:
                GC += SeqRecord.seq.upper().count("G")
                GC += SeqRecord.seq.upper().count("C")

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

        self._seqstats = SeqStats(
            number_seqs, total_bps, mean_bp, min_bp, max_bp, N50, GC
        )

        for k, value in self._seqstats.__dict__.items():
            setattr(self, k, value)

        return self._seqstats


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


def seqrecordgenerator(path, format, parser="seq", warnings=False):
    """
    :param path: Path to file.
    :param format: format to pass to SeqIO.parse().
    :param parser: Whether to import records with SeqIO (default) or AlignIO
    :param warnings: Whether to warn if sha1 checksum differs or file does not exist.

    :return: A generator of SeqRecords.
    """
    parser_l = parser.lower()
    available_parsers = ("seq", "align")
    assert parser in available_parsers, Warnings()["choices"](
        parser, available_parsers, "parser"
    )
    kind_dict = {
        "seq": lambda _path, _format: SeqIO.parse(path, format=format),
        "align": lambda _path, _format: AlignIO.parse(path, format=format),
    }
    try:
        records = kind_dict[parser_l](path, format)
        return records
    except FileNotFoundError:
        if warnings:
            print(Warnings()["not_exist"](path))
            print(
                "The file was loaded as a BioProv object, but it does not exist on the specified path."
            )
        return None


def deserialize_files_dict(files_dict):
    """
    Deserialize a dictionary of files in JSON format.
    :param files_dict: dict of dicts.
    :return: dict of File instances.
    """
    for tag, file in files_dict.items():
        if file is not None:
            if "format" in file.keys():
                if file["format"] in SeqFile.seqfile_formats:
                    # To-do: don't import records again (slow)
                    # Get them straight from the JSON file.
                    files_dict[tag] = SeqFile(
                        path=file["path"],
                        tag=file["tag"],
                    )
                    _ = files_dict[tag].generator
                    for seqstats_attr_ in SeqStats.__dataclass_fields__.keys():
                        if seqstats_attr_ in file.keys():
                            setattr(
                                files_dict[tag],
                                seqstats_attr_,
                                file[seqstats_attr_],
                            )
            else:
                files_dict[tag] = File(file["path"], tag=file["tag"])
            for attr_, value_ in file.items():
                if attr_ not in ("path",):
                    setattr(files_dict[tag], attr_, value_)
    return files_dict
