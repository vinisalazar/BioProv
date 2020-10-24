__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Init module for package bioprov.

Inherits objects from the src/ package.
"""

from .src.config import config, EnvProv, BioProvDB
from .src.files import File, SeqFile
from .src.main import (
    Program,
    PresetProgram,
    Parameter,
    Run,
    Sample,
    Project,
    read_csv,
    from_df,
    from_json,
    write_json,
)
from .src.prov import BioProvDocument, BioProvDocument

name = "bioprov"
