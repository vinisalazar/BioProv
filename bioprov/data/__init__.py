"""
Contains example and test data.
"""

from pathlib import Path

data_dir = Path(__file__).parent
genomes_dir = Path.joinpath(data_dir, "genomes")
datasets_dir = Path.joinpath(data_dir, "datasets")
synechococcus_genome = Path.joinpath(
    genomes_dir, "GCF_000010065.1_ASM1006v1_genomic.fna"
)

# To-do: Join these two as the same
# Refactor genome_annotation so it takes a dataset same as 'synechococcus.csv'
synechococcus_dataset = Path.joinpath(datasets_dir, "synechococcus.csv")
genome_annotation_dataset = Path.joinpath(datasets_dir, "genome_annotation_input.tsv")
