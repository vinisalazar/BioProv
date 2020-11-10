#!/usr/bin/env python
__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"

"""
BLAST nucleotide alignment workflow

'Align nucleotide data to a reference database with BLASTN'

This can be run by itself as a script or called
with the BioProv CLI application (recommended).
"""

from bioprov.programs import blastn
from bioprov.src.workflow import Workflow, Step


def blastn_alignment(**kwargs):

    _blastn_alignment = Workflow(
        name="blastn",
        description="Align nucleotide data to a reference database with BLASTN.",
        input_type="dataframe",
        index_col="sample-id",
        file_columns="query",
        **kwargs,
    )

    try:
        _blastn_alignment.db = kwargs["db"]
    except KeyError:
        _blastn_alignment.db = None

    blastn_preset = blastn(db=_blastn_alignment.db)

    _blastn_alignment.add_step(Step(blastn_preset, default=True))

    # Workflow specific arguments must be added AFTER the steps.
    # That is because adding a Step updates the parser with the default arguments
    # of the Workflow class.

    _blastn_alignment.parser.add_argument(
        "-db",
        "--database",
        help="BLASTn reference database. Must be a valid BLAST database created with the `makeblastdb` command.",
        required=True,
    )

    return _blastn_alignment
