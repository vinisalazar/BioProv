"""
Testing for the workflows package.
"""

from argparse import Namespace
from bioprov.data import genome_annotation_dataset
from bioprov.workflows import GenomeAnnotation
from bioprov import config


def test_GenomeAnnotation():
    genome_annotation = GenomeAnnotation()
    _ = genome_annotation.parser()
    args = Namespace
    args.input = genome_annotation_dataset
    args.label = "label"
    args.files = "path"
    args.tag = "Synechococcus_elongatus_PCC_6301"
    args.run_prokka = False
    args.skip_prodigal = False
    args.verbose = True
    args.threads = config.threads
    _ = genome_annotation.main(
        _input_path=args.input,
        labels=args.label,
        files=args.files,
        _tag=args.tag,
        run_prokka=args.run_prokka,
        _skip_prodigal=args.skip_prodigal,
        _verbose=args.verbose,
        _threads=args.threads,
    )
