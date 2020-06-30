"""
Testing module for drafting new ideas.

To-do:
    - create classes Sample, Process
"""

import bioprov as bp
from subprocess import Popen, PIPE


def test_pipeline():
    assembly_file_path = str(bp.genomes_dir) + "/GCF_000010065.1_ASM1006v1_genomic.fna"
    name, tag = "Synechococcus elongatus PCC 6301", "GCF_000010065.1"
    assembly_file = bp.SequenceFile(assembly_file_path, "assembly")
    protein_file = bp.File(
        assembly_file_path.replace(".fna", "_proteins.faa"), "proteins"
    )
    sample = bp.Sample(
        name,
        tag,
        {"assembly": assembly_file},
        {"description": f"Genome of {name} with RefSeq accession {tag}"},
    )
    sample.add_file(protein_file)
    assert assembly_file.exists, sample.files["assembly"].exists
    program, version = "prodigal", "v2.6.3"
    program = bp.Program(program, version=version)
    param_i = bp.Parameter(
        "-i", str(assembly_file), description="assembly", kind="input"
    )
    param_a = bp.Parameter(
        "-a", str(protein_file), description="proteins", kind="output",
    )
    program.add_parameter(param_i)
    program.add_parameter(param_a)
    p = Popen(program.cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (stdin, stdout, stderr) = (p.stdin, p.stdout, p.stderr)
    return sample, program, p, (stdin, stdout, stderr)


genome, program, p, (stdin, stdout, stderr) = test_pipeline()
