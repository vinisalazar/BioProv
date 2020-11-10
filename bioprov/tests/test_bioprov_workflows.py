__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


"""
Testing for the workflows package.
"""
from os import remove
from pathlib import Path
from bioprov.data import genome_annotation_dataset
from bioprov.utils import Warnings
from bioprov.workflows.blastn import blastn_alignment
from bioprov.workflows.genome_annotation import genome_annotation
from bioprov.workflows.kaiju import KaijuWorkflow


def test_blastn_workflow():

    workflow = blastn_alignment()

    blastn_step = workflow.steps["blastn"].serializer()

    default_param_str = "-db None -outfmt 6"

    assert blastn_step["param_str"] == default_param_str


def test_genome_annotation():
    """
    Tests the 'genome_annotation' workflow with the 'prodigal' step.
    :return:
    """
    workflow = genome_annotation(tag="test-project")
    workflow.input = genome_annotation_dataset
    steps = [
        "prodigal",
    ]
    workflow.run_steps(steps)

    for _, sample in workflow.project.items():
        for key, file in sample.files.items():
            assert file.exists, Warnings()["not_exist"](file.path)

    log_file = "test-project.log"
    assert Path(log_file).exists()
    remove(log_file)


def test_kaiju_workflow():
    """
    Tests the 'kaiju' workflow.
    :return:
    """
    _ = KaijuWorkflow()
    pass
