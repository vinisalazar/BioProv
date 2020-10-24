__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Module for holding preset instances of the Program class.
"""

from os import path
from bioprov import config, File
from bioprov.src.main import Parameter, Program, PresetProgram
from bioprov.utils import assert_tax_rank, Warnings


def prodigal(sample=None, input_tag="assembly"):
    """
    :param sample: Instance of BioProv.Sample.
    :param input_tag: Instance of BioProv.Sample.
    :return: Instance of PresetProgram containing Prodigal.
    """
    _prodigal = PresetProgram(
        name="prodigal",
        sample=sample,
        input_files={"-i": input_tag},
        output_files={
            "-a": ("proteins", "_proteins.faa"),
            "-d": ("genes", "_genes.fna"),
            "-s": ("scores", "_scores.cds"),
        },
        preffix_tag=input_tag,
    )

    return _prodigal


def prokka_():
    """
    :return: Instance of PresetProgram containing Prokka.
    """
    _prokka = PresetProgram(program=Program("prokka"))  # no cover


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
    prefix = _sample.name.replace(" ", "_")
    if output_path is None:
        output_path = path.join(
            str(_sample.files[assembly].directory), f"{prefix}_prokka"
        )

    _prokka = Program(
        "prokka",
    )
    params = (
        Parameter(key="--prefix", value=prefix, kind="misc"),
        Parameter(key="--outdir", value=output_path, kind="output"),
        Parameter(key="--cpus", value=threads, kind="misc"),
    )

    for param in params:
        _prokka.add_parameter(param, _print=False)

    if path.isdir(output_path):
        print(f"Warning: {output_path} directory exists. Will overwrite.")  # no cover
        _prokka.add_parameter(
            Parameter(key="--force", value="", kind="misc")
        )  # no cover

    # Add files according to their extension # To-do: add support for SeqFile
    extensions_parser = {
        ".faa": lambda file: _sample.add_files(File(file, tag=proteins)),
        ".fna": lambda file: _sample.add_files(File(file, tag=contigs)),
        ".ffn": lambda file: _sample.add_files(File(file, tag=genes)),
        ".fsa": lambda file: _sample.add_files(File(file, tag=submit_contigs)),
        ".tbl": lambda file: _sample.add_files(File(file, tag=feature_table)),
        ".sqn": lambda file: _sample.add_files(File(file, tag=sequin)),
        ".gbk": lambda file: _sample.add_files(File(file, tag=genbank)),
        ".gff": lambda file: _sample.add_files(File(file, tag=gff)),
        ".log": lambda file: _sample.add_files(File(file, tag=log)),
        ".txt": lambda file: _sample.add_files(File(file, tag=stats)),
    }

    for ext, func in extensions_parser.items():
        file_ = path.join(path.abspath(output_path), _sample.name + ext)
        _ = func(file_)  # Add file based on extension

    if add_param_str:  # Any additional parameters are added here.
        _prokka.cmd += f" {add_param_str}"  # no cover

    # Input goes here, must be last positionally.
    _prokka.add_parameter(
        Parameter(key="", value=str(_sample.files[assembly]), kind="input"),
        _print=False,
    )

    return _prokka


def kaiju(
    _sample,
    output_path=None,
    kaijudb="",
    nodes="",
    threads=config.threads,
    r1="R1",
    r2="R2",
    add_param_str="",
):
    """
    Run Kaiju on paired-end metagenomic data.

    :param _sample: An instance of BioProv sample.
    :param output_path: Output file of Kaiju.
    :param kaijudb: Path to Kaiju database.
    :param nodes: Nodes file to use with Kaiju.False
    :param threads: Threads to use with Kaiju.
    :param r1: Tag of forward reads.
    :param r2: Tag of reverse reads.
    :param add_param_str: Add any paremeters to Kaiju.
    :return: An instance of Program, containing Kaiju.
    """
    kaiju_out_name = _sample.name + "_kaiju.out"
    if output_path is None:
        output_path = path.join(
            _sample.files[r1].directory,
            kaiju_out_name,
        )
    else:
        output_path = path.join(output_path, kaiju_out_name)  # no cover
    _sample.add_files(File(output_path, tag="kaiju_output"))

    kaiju_ = Program("kaiju")

    params = (
        Parameter(key="-t", value=nodes, kind="misc"),
        Parameter(key="-i", value=str(_sample.files[r1]), kind="input"),
        Parameter(key="-j", value=str(_sample.files[r2]), kind="input"),
        Parameter(key="-f", value=kaijudb, kind="input"),
        Parameter(key="-z", value=threads, kind="misc"),
        Parameter(key="-o", value=output_path, kind="output"),
    )
    for p in params:
        kaiju_.add_parameter(p, _print=False)

    if add_param_str:
        kaiju_.cmd += f" {add_param_str}"  # no cover

    return kaiju_


def kaiju2table(
    _sample,
    output_path=None,
    rank="phylum",
    nodes="",
    names="",
    kaiju_output="kaiju_output",
    add_param_str="",
):
    """
    Run kaiju2table to create Kaiju reports.
    :param _sample: An instance of BioProv sample.
    :param output_path: Output file of kaiju2table.
    :param rank: Taxonomic rank to create report of.
    :param nodes: Nodes file to use with kaiju2table.
    :param names: Names file to use with kaiju2table.
    :param kaiju_output: Tag of Kaiju output file.
    :param add_param_str: Parameter string to add.
    :return: Instance of Program containing kaiju2table.
    """
    # Assertion statement for rank argument.
    assert_tax_rank(rank), Warnings()["invalid_tax_rank"](rank)

    kaiju_report_suffix = f"kaiju_report_{rank}"
    kaiju_report_out = f"{_sample.name}_{kaiju_report_suffix}"

    # Format output_path
    if output_path is None:
        output_path = path.join(
            _sample.files[kaiju_output].directory, kaiju_report_out + ".tsv"
        )
    _sample.add_files(File(output_path, tag=kaiju_report_suffix))

    kaiju2table_ = Program("kaiju2table")
    params = (
        Parameter("-o", str(_sample.files[kaiju_report_suffix]), kind="output"),
        Parameter("-t", nodes, kind="misc"),
        Parameter("-n", names, kind="misc"),
        Parameter("-r", rank, kind="misc"),
    )

    for p in params:
        kaiju2table_.add_parameter(p, _print=False)

    # Add final parameter:
    kaiju2table_.cmd += f" {str(_sample.files[kaiju_output])}"

    if add_param_str:
        kaiju2table_.cmd += f" {add_param_str}"  # no cover

    return kaiju2table_
