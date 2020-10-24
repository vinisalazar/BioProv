__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Testing module for the package BioProv.

Tests include:
    - Imports;
    - Class generation and methods.
"""


def test_import_bioprov():
    """
    Test if the package can be imported correctly.
    :return: ImportError if not able to import.
    """
    import bioprov as bp

    del bp


def test_import_classes_and_functions():
    """
    Test if all classes and functions can be imported correctly.
    :return: ImportError if not able to import
    """
    from bioprov import (
        BioProvDocument,
        config,
        EnvProv,
        File,
        Program,
        Parameter,
        Run,
        Sample,
        Project,
        read_csv,
        from_df,
        from_json,
        SeqFile,
    )

    del (
        BioProvDocument,
        config,
        EnvProv,
        File,
        Program,
        Parameter,
        Run,
        Sample,
        Project,
        read_csv,
        from_df,
        from_json,
        SeqFile,
    )


def test_import_packages():
    """
    Test if supplementary packages can be imported correctly.
    :return: ImportError if not able to import
    """
    from bioprov import src, data, programs, workflows, bioprov
    from bioprov.data import (
        data_dir,
        genomes_dir,
        synechococcus_genome,
        picocyano_dataset,
    )
    from bioprov.programs import prodigal, prokka, kaiju, kaiju2table
    from bioprov.workflows import (
        KaijuWorkflow,
        genome_annotation,
        WorkflowOptionsParser,
    )

    del src, data, programs, workflows, bioprov
    del (
        data_dir,
        genomes_dir,
        synechococcus_genome,
        picocyano_dataset,
    )
    del prodigal, prokka, kaiju, kaiju2table
    del (
        KaijuWorkflow,
        genome_annotation,
        WorkflowOptionsParser,
    )
