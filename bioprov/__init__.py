__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.2"


"""
Init module for package bioprov.

Inherits objects from the src/ package.
"""

from .src.config import Config, default_config
from .src.files import File, SeqFile
from .src.program import (
    Program,
    PresetProgram,
    Parameter,
    Run,
    Sample,
    Project,
    read_csv,
    from_df,
    from_json,
)
from .src.prov import BioProvDocument, BioProvProject

name = "bioprov"
