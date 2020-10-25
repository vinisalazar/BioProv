#!/usr/bin/env python
__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"

"""
BLAST nucleotide alignment workflow

'Align nucleotide data to a reference database with BLASTN'

This can be run by itself as a script or called
with the BioProv CLI application (recommended).
"""

from bioprov.src.workflow import Workflow
from bioprov.programs import blastn


def blastn_workflow(**kwargs):
    pass


if __name__ == "__main__":
    pass
