__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Integration testing for drafting new ideas.
"""

import bioprov as bp
from os import remove


def test_integration(debug=False):
    """
    Tests an example pipeline of running Prodigal.
    :return:
    """

    # Build Sample with Files
    assembly_file = bp.data.synechococcus_genome
    protein_file = str(assembly_file).replace("fna", "faa")
    name, tag = "Synechococcus elongatus PCC 6301", "GCF_000010065.1"
    assembly_file = bp.SequenceFile(assembly_file, "assembly")
    sample = bp.Sample(  # Add one file in the __init__ method
        name,
        tag,
        {"assembly": assembly_file},
        {"description": f"Genome of {name} with RefSeq accession {tag}"},
    )
    protein_file = bp.SequenceFile(protein_file, "proteins")
    sample.add_files(protein_file)  # And add another file with the add_file method
    assert assembly_file.exists, sample.files["assembly"].exists

    # Build Program with parameters
    program_name, version = "prodigal", "v2.6.3"
    param_i = bp.Parameter(
        "-i", str(assembly_file), description="assembly", kind="input"
    )
    program_ = bp.Program(
        program_name, params=param_i, version=version
    )  # Add one parameter with __init__ method
    param_a = bp.Parameter(
        "-a", str(protein_file), description="proteins", kind="output",
    )
    program_.add_parameter(param_i), program_.add_parameter(
        param_a
    )  # And another with add_file()

    # Run Program on sample
    _ = program_.run(sample=sample)
    run = program_.run_

    # Assert block
    assert protein_file.exists
    assert run.status is "Finished"

    # Clean up
    remove(str(sample.files["proteins"]))

    # Return (useful for debugging)
    if debug:
        return sample, program_, run


# Uncomment this if you want to test locally
# genome, program, run_ = test_integration(debug=True)
