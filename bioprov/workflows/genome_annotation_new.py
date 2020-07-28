#!/usr/bin/env python
__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"

"""
Genome annotation workflow module.

'Genome annotation with Prodigal, Prokka and the COG database.'

This can be run by itself as a script or called
with the BioProv CLI application (recommended).
"""

from bioprov.src.workflow import Workflow, Step
from bioprov.programs import prodigal, prokka


def genome_annotation(**kwargs):
    _genome_annotation = Workflow(
        name="genome_annotation",
        description="Genome annotation with Prodigal, Prokka and the COG database.",
        **kwargs
    )

    # Create steps from preset programs.
    prodigal_preset, prokka_preset = prodigal(), None
    steps = [
        Step(prodigal_preset, default=True, run=True),
    ]

    # Add steps to parser
    for step in steps:
        _genome_annotation.add_step(step)

    return _genome_annotation


if __name__ == "__main__":
    workflow = genome_annotation()
    parser = workflow.parser
    args = parser.parse_args()
    workflow.input = args.input
    workflow.input_type = args.input_type

    # Change behaviour of steps based on command line arguments.
    for k, step in workflow.steps.items():
        if step.default:
            step.run = eval("args.skip_{}".format(step.name))
        else:
            step.run = eval("args.run_{}".format(step.name))

    workflow.run_steps()
