"""
Testing module for drafting new ideas.

To-do:
    - create classes Sample, Process
"""

import bioprov as bp
from subprocess import Popen, PIPE


def test_pipeline():
    genome_path = str(bp.genomes_dir) + "/GCF_000010065.1_ASM1006v1_genomic.fna"
    tag = "Synechococcus elongatus PCC 6301"
    genome = bp.SequenceFile(genome_path, tag)
    # sample = Sample(tag, files={"assembly": genome})
    assert genome.exists
    program, version = "prodigal", "v2.6.3"
    program = bp.Program(program, version=version)
    param_i = bp.Parameter("-i", genome_path, description="assembly", kind="input")
    param_a = bp.Parameter(
        "-a",
        str(genome.path).replace(".fna", "_proteins.faa"),
        description="proteins",
        kind="output",
    )
    program.add_parameter(param_i)
    program.add_parameter(param_a)
    p = Popen(program.cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (stdin, stdout, stderr) = (p.stdin, p.stdout, p.stderr)
    return genome, program, p, (stdin, stdout, stderr)


genome, program, p, (stdin, stdout, stderr) = test_pipeline()
