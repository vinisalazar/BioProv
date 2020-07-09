"""
Module for holding preset instances of the Program class.
"""

from os import listdir, path
from bioprov import Program, Parameter, File
from bioprov import config


def prodigal(
    _sample,
    assembly="assembly",
    genes="genes",
    proteins="proteins",
    scores="scores",
    write_scores=False,
):
    """
    :param _sample: An instance of BioProv Sample.
    :param assembly: Name of assembly file.
    :param genes: Name of genes file.
    :param proteins: Name of proteins file.
    :param scores: Name of scores file.
    :param write_scores: bool Whether to write the scores file. Default is False because they are BIG.
    :return:
    """
    file_preffix = str(_sample.files[assembly].path)
    _sample.add_files(
        {
            proteins: file_preffix + "_proteins.faa",
            genes: file_preffix + "_genes.fna",
            scores: file_preffix + "_score.cds",
        }
    )
    prodigal_ = Program("prodigal",)
    params = (
        Parameter(key="-i", value=str(_sample.files[assembly]), kind="input"),
        Parameter(key="-a", value=str(_sample.files[proteins]), kind="output"),
        Parameter(key="-d", value=str(_sample.files[genes]), kind="output"),
        Parameter(key="-s", value=str(_sample.files[scores]), kind="output"),
    )
    for param in params:
        if param.key == "-s":
            if not write_scores:
                pass
        prodigal_.add_parameter(param, _print=False)

    return prodigal_


def prokka(
    _sample,
    output_path=None,
    threads=config.threads,
    add_param_str="",
    assembly="assembly",
    contigs="prokka_contigs",
    genes="prokka_genes",
    proteins="prokka_proteins",
    feature_table="feature_table",
    submit_contigs="submit_contigs",
    sequin="sequin",
    genbank="genbank",
    gff="gff",
    log="prokka_log",
    stats="prokka_stats",
):
    """
    :param _sample: An instance of BioProv Sample.
    :param output_path: Output directory of Prokka.
    :param threads: Threads to use for Prokka.
    :param add_param_str: Any additional parameters to be passed to Prokka (in string format)

    The following params are the tags for each file, meaning that they are a string
    present in _sample.files.keys().

    :param assembly: Input assembly file.
    :param contigs: Output contigs.
    :param genes: Output genes.
    :param proteins: Output proteins.
    :param feature_table Output feature table.
    :param submit_contigs: Output contigs formatted for NCBI submission.
    :param sequin: Output sequin file.
    :param genbank: Output genbank .gbk file
    :param gff: Output .gff file
    :param log: Prokka log file.
    :param stats: Prokka stats file.
    :return: An instance of Program, containing Prokka.
    """

    # Default output is assembly file directory.
    if output_path is None:
        output_path = path.join(
            str(_sample.files[assembly].directory), "{}_prokka".format(_sample.name)
        )

    prokka_ = Program("prokka",)
    params = (
        Parameter(key="--prefix", value=_sample.name, kind="misc"),
        Parameter(key="--output", value=output_path, kind="output"),
        Parameter(key="--cpus", value=threads, kind="misc"),
    )

    for param in params:
        prokka_.add_parameter(param, _print=False)

    # Add files according to their extension
    extensions_parser = {
        ".faa": lambda file: _sample.add_file(File(file, tag=proteins)),
        ".fna": lambda file: _sample.add_file(File(file, tag=contigs)),
        ".ffn": lambda file: _sample.add_file(File(file, tag=genes)),
        ".fsa": lambda file: _sample.add_file(File(file, tag=submit_contigs)),
        ".tbl": lambda file: _sample.add_file(File(file, tag=feature_table)),
        ".sqn": lambda file: _sample.add_file(File(file, tag=sequin)),
        ".gbk": lambda file: _sample.add_file(File(file, tag=genbank)),
        ".gff": lambda file: _sample.add_file(File(file, tag=gff)),
        ".log": lambda file: _sample.add_file(File(file, tag=log)),
        ".txt": lambda file: _sample.add_file(File(file, tag=stats)),
    }

    for file_ in listdir(output_path):
        file_ = path.join(path.abspath(output_path), file_)
        _, ext = path.splitext(file_)
        _ = extensions_parser[ext]  # Add file based on extension

    if add_param_str:  # Any additional parameters are added here.
        prokka_.cmd += " {}".format(add_param_str)

    # Input goes here, must be last positionally.
    prokka_.add_parameter(
        Parameter(key="", value=_sample.files[assembly], kind="input")
    )

    return prokka_
