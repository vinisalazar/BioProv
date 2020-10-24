__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Testing for the workflows package.
"""
from bioprov.data import genome_annotation_dataset
from bioprov.workflows.genome_annotation import genome_annotation
from bioprov.workflows.kaiju import KaijuWorkflow


def test_genome_annotation():
    """
    Tests the 'genome_annotation' workflow with the 'prodigal' step.
    :return:
    """
    workflow = genome_annotation()
    workflow.input = genome_annotation_dataset
    steps = [
        "prodigal",
    ]
    workflow.run_steps(steps)


def test_kaiju_workflow():
    """
    Tests the 'kaiju' workflow.
    :return:
    """
    _ = KaijuWorkflow()
    pass
