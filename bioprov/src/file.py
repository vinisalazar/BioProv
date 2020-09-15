__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.1"


"""
Contains the File class and related functions.
"""
from pathlib import Path
from Bio import SeqIO
from bioprov.utils import get_size
from prov.model import ProvEntity


class File:
    """
    Class for holding file and file information.
    """

    def __init__(
        self, path, tag=None, document=None,
    ):
        """
        :param path: A UNIX-like file path.
        :param tag: optional tag describing the file.
        :param document: prov.model.ProvDocument
        """
        self.path = Path(path).absolute()
        self.name = self.path.stem
        self.basename = self.path.name
        self.directory = self.path.parent
        self.extension = self.path.suffix
        if tag is None:
            tag = self.name
        self.tag = tag
        self.exists = self.path.exists()
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


class FASTAFile(File):
    """
    Class for holding sequence file and sequence information. Inherits from File.
    """

    def __init__(
        self, path, tag=None, document=None, import_records=True, _format="fasta",
    ):
        """
        :param path: A UNIX-like file path.
        :param tag: optional tag describing the file.
        :param import_records: Whether to import sequence data as Bio.SeqRecord.SeqRecord
        :param _format: Input format. Only 'fasta' is supported for now.
        """
        super().__init__(path, tag, document)
        self._generator = None
        self.records = None

        if self.exists:
            self.fasta_seqrecordgenerator()
        else:
            import_records = False

        if import_records:
            self.import_records()

    def fasta_seqrecordgenerator(self):
        """
        Runs seqrecordgenerator with the FASTA format.
        """
        self._generator = seqrecordgenerator(self.path, "fasta")

    @property
    def generator(self):
        if self._generator is None:
            self.fasta_seqrecordgenerator()
        return self._generator

    @generator.setter
    def generator(self, value):
        self._generator = value

    def import_records(self):
        self.records = SeqIO.to_dict(self._generator)


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
