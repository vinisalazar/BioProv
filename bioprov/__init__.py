__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


"""
Init module for package bioprov.

Inherits objects from the src/ package.
"""

from .src.config import config, Environment, BioProvDB
from .src.files import File, SeqFile, Directory
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
    load_project,
)
from .src.prov import BioProvDocument, BioProvDocument

name = "bioprov"
