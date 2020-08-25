__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Contains example and test data.
"""

from pathlib import Path
from bioprov.src.sample import Sample

data_dir = Path(__file__).parent
genomes_dir = Path.joinpath(data_dir, "genomes")
datasets_dir = Path.joinpath(data_dir, "datasets")
synechococcus_genome = Path.joinpath(
    genomes_dir, "GCF_000010065.1_ASM1006v1_genomic.fna"
)
synechococcus_sample = Sample(
    "GCF_000010065.1_ASM1006v1",
    files={"assembly": synechococcus_genome},
    tag="Synechococcus_elongatus_PCC_6301",
)

# To-do: Join these two as the same
# Refactor genome_annotation so it takes a dataset same as 'picocyano.csv'
picocyano_dataset = Path.joinpath(datasets_dir, "picocyano.csv")
genome_annotation_dataset = Path.joinpath(datasets_dir, "genome_annotation_input.tsv")
