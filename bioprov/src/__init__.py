"""
Init file for the src/ package. Contains the main modules.
"""

from .Config import Config, config
from .File import File
from .Program import Program, Parameter, Run, parse_params, generate_param_str
from .Sample import (
    Sample,
    SampleSet,
    read_csv,
    from_df,
    from_json,
    dict_to_sample,
    json_to_dict,
)
from .SequenceFile import SequenceFile, seqrecordgenerator, seqstats
