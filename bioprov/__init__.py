__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.1"


"""
Init module for package bioprov.

Inherits objects from the src/ package.
"""

from .src.config import Config, default_config
from .src.files import File, SeqFile
from .src.program import Program, Parameter, Run
from .src.sample import (
    Sample,
    Project,
    read_csv,
    from_df,
    from_json,
)

name = "bioprov"
