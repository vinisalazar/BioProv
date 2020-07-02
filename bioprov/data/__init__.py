"""
Contains example and test data.
"""

from pathlib import Path

data_dir = Path(__file__).parent
genomes_dir = Path.joinpath(data_dir, "genomes")
synechococcus_genome = Path.joinpath(
    genomes_dir, "GCF_000010065.1_ASM1006v1_genomic.fna"
)
