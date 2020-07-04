"""
Init module for package bioprov.

Inherits objects from the src/ package.
"""

from src.Config import Config, config
from src.File import File
from src.Program import Program, Parameter, Run
from src.Sample import Sample, SampleSet, read_csv, from_df
from src.SequenceFile import SequenceFile, seqrecordgenerator

name = "bioprov"
