#!/usr/bin/env python
__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"

"""
Genome annotation workflow module.

'Genome annotation with Prodigal, Prokka and the COG database.'

This can be run by itself as a script or called
with the BioProv CLI application (recommended).
"""

from bioprov.src.workflow import Workflow, Step
from bioprov.programs import prodigal  # , prokka


def genome_annotation(**kwargs):
    _genome_annotation = Workflow(
        name="genome_annotation",
        description="Genome annotation with Prodigal, Prokka and the COG database.",
        input_type="dataframe",
        index_col="sample-id",
        file_columns="assembly",
        **kwargs,
    )

    # Create steps from preset programs.
    prodigal_preset, prokka_preset = (prodigal(), None)  # prokka()
    steps = [
        Step(prodigal_preset, default=True),
        # Step(prokka_preset, default=False),
    ]

    # Add steps to parser
    for _step in steps:
        _genome_annotation.add_step(_step)

    return _genome_annotation


if __name__ == "__main__":
    workflow = genome_annotation()
    workflow.main()
