__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


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
        Environment,
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
        Environment,
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
        megares_blastdb,
    )
    from bioprov.programs import prodigal, diamond, prokka, kaiju, kaiju2table, blastn
    from bioprov.workflows import (
        KaijuWorkflow,
        genome_annotation,
        WorkflowOptionsParser,
        blastn_alignment,
    )

    del src, data, programs, workflows, bioprov
    del (
        data_dir,
        genomes_dir,
        synechococcus_genome,
        picocyano_dataset,
        megares_blastdb,
    )
    del prodigal, diamond, prokka, kaiju, kaiju2table, blastn
    del (KaijuWorkflow, genome_annotation, WorkflowOptionsParser, blastn_alignment)
