__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Integration testing for drafting new ideas.
"""

from argparse import Namespace
import bioprov as bp
import pytest
from os import remove
from bioprov.data import picocyano_dataset


def test_integration(debug=False):
    """
    Tests an example pipeline of running Prodigal.
    :return:
    """

    # Build Sample with Files
    assembly_file = bp.data.synechococcus_genome
    protein_file = str(assembly_file).replace("fna", "faa")
    name, tag = "Synechococcus elongatus PCC 6301", "GCF_000010065.1"
    assembly_file = bp.SeqFile(assembly_file, "assembly")
    sample = bp.Sample(  # Add one file in the __init__ method
        name,
        tag,
        {"assembly": assembly_file},
        {"description": f"Genome of {name} with RefSeq accession {tag}"},
    )
    protein_file = bp.SeqFile(protein_file, "proteins")
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
        "-a",
        str(protein_file),
        description="proteins",
        kind="output",
    )
    program_.add_parameter(param_i), program_.add_parameter(
        param_a
    )  # And another with add_file()

    # Run Program on sample
    run_ = program_.run(sample=sample)

    # Assert block
    assert protein_file.exists
    assert run_.status is "Finished"

    # Clean up
    remove(str(sample.files["proteins"]))

    # Return (useful for debugging)
    if debug:
        return sample, program_, run_


def test_CLI():
    from bioprov.bioprov import main

    # https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type == SystemExit

    # Test other arguments
    args = Namespace(show_config=True)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main(args)

    assert pytest_wrapped_e.type == SystemExit

    args = Namespace(subparser_name="genome_annotation", show_config=False)
    with pytest.raises(AttributeError) as pytest_wrapped_e:
        main(args)

    assert pytest_wrapped_e.type == AttributeError
