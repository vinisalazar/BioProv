__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Init module for package bioprov.

Inherits objects from the src/ package.
"""

from .src.Config import Config, default_config
from .src.File import File
from .src.Program import Program, Parameter, Run
from .src.Sample import (
    Sample,
    SampleSet,
    read_csv,
    from_df,
    from_json,
)
from .src.SequenceFile import SequenceFile

name = "bioprov"
