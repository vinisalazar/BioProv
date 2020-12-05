__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


"""
Module for holding preset instances of the Program class.
Module for holding preset instances of the Program class.
"""

import logging
from os import path
from pathlib import Path

from bioprov import File, config
from bioprov.src.main import Parameter, PresetProgram, Program
from bioprov.utils import Warnings, assert_tax_rank


def diamond(blast_type, sample, db, query_tag="query", outformat=6, extra_flags=None):
    """
    :param str blast_type: Which aligner to use ('blastp' or 'blastx').
    :param Sample sample: Instance of BioProv.Sample.
    :param str db: A string pointing to the reference database path.
    :param str query_tag: A tag for the query file.
    :param int outformat: The output format to gather from diamond (0, 5 or 6).
    :param list extra_flags: A list of extra parameters to pass to diamond
        (e.g. --sensitive or --log).
    :return: Instance of PresetProgram containing Diamond.
    :rtype: BioProv.PresetProgram.
    """

    _diamond = PresetProgram(
        name="diamond",
        params=(
            Parameter(key=blast_type),
            Parameter(key="--db", value=db),
            Parameter(key="--outfmt", value=outformat),
        ),
        sample=sample,
        input_files={"--query": query_tag},
        output_files={"--out": ("_dmnd_hits", "_dmnd_hits.tsv")},
        extra_flags=extra_flags,
    )

    return _diamond


def prodigal(sample=None, input_tag="assembly", extra_flags=None):
    """
    :param sample: Instance of BioProv.Sample.
    :param input_tag: Instance of BioProv.Sample.
    :param list extra_flags: A list of extra parameters to pass to Prodigal.
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
        extra_flags=extra_flags,
    )

    return _prodigal


def _create_blast_preset(blast_type, sample, db, query_tag, outformat, extra_flags):
    """
    :param str blast_type: What BLAST program to build (e.g. 'blastn');
    :return: Instance of PresetProgram for the chosen blast program type.
    :rtype: BioProv.PresetProgram.
    """

    if db is not None:
        db_dir = Path(db).parent.is_dir()
        assert db_dir, "Path to the reference database does not exist"

    _blast_program = PresetProgram(
        name=blast_type,
        params=(
            Parameter(key="-db", value=db),
            Parameter(key="-outfmt", value=outformat),
        ),
        sample=sample,
        input_files={"-query": query_tag},
        output_files={"-out": (f"{blast_type}_hits", f"_{blast_type}_hits.txt")},
        extra_flags=extra_flags,
    )

    return _blast_program


def blastn(sample=None, db=None, query_tag="query", outformat=6, extra_flags=None):
    """
    :param Sample sample: Instance of BioProv.Sample.
    :param str db: A string pointing to the reference database directory and title.
    :param str query_tag: A tag for the query file.
    :param int outformat: The output format to gather from blastn.
    :param list extra_flags: A list of extra parameters to pass to BLASTN.
    :return: Instance of PresetProgram for BLASTN.
    :rtype: BioProv.PresetProgram.
    :raises AssertionError: Path to the reference database does not exist.
    """

    _blastn = _create_blast_preset(
        "blastn", sample, db, query_tag, outformat, extra_flags
    )

    return _blastn


def blastp(sample, db, query_tag="query", outformat=6, extra_flags=None):
    """
    :param Sample sample: Instance of BioProv.Sample.
    :param str db: A string pointing to the reference database directory and title.
    :param str query_tag: A tag for the query file.
    :param int outformat: The output format to gather from blastp.
    :param list extra_flags: A list of extra parameters to pass to BLASTP.
    :return: Instance of PresetProgram for BLASTP.
    :rtype: BioProv.PresetProgram.
    :raises AssertionError: Path to the reference database does not exist.
    """

    _blastp = _create_blast_preset(
        "blastp", sample, db, query_tag, outformat, extra_flags
    )

    return _blastp


def muscle(sample, input_tag="input", msf=False, extra_flags=None):
    """
    :param Sample sample: Instance of BioProv.Sample.
    :param str input_tag: A tag for the input multi-fasta file.
    :param bool msf: Whether or not to have the output in msf format.
    :param list extra_flags: A list of extra parameters to pass to Muscle.
    :return: Instance of PresetProgram for Muscle.
    :rtype: BioProv.PresetProgram.
    """

    _muscle = PresetProgram(
        name="muscle",
        sample=sample,
        input_files={"-in": input_tag},
        output_files={"-out": ("_muscle_hits", "_muscle_hits.afa")},
        extra_flags=extra_flags,
    )

    if msf:
        _muscle.add_parameter(Parameter(key="-msf"))

    return _muscle


def mafft(sample, input_tag="input", extra_flags=None):
    """
    :param Sample sample: Instance of BioProv.Sample.
    :param str input_tag:  A tag for the input fasta file.
    :param list extra_flags: A list of extra parameters to pass to MAFFT.
    :return: Instance of PresetProgram containing MAFFT.
    :rtype: BioProv.PresetProgram.
    """
    _mafft = PresetProgram(
        name="mafft",
        sample=sample,
        input_files={"": input_tag},
        output_files={">": ("aligned", "_aligned.afa")},
        preffix_tag=input_tag,
        extra_flags=extra_flags,
    )

    return _mafft


def kallisto_quant(sample, index, output_dir="./", extra_flags=None):
    """
    Run kallisto's alignment and quantification

    :param Sample sample: Instance of BioProv.Sample.
    :param str index: A path to a kallisto index file.
    :param str output_dir: A path to kallisto's output directory.
    :param list extra_flags: A list of extra parameters to pass to kallisto
        (e.g. --single or --plaintext).
    :return: Instance of PresetProgram containing kallisto.
    :rtype: BioProv.PresetProgram.
    """

    _kallisto = PresetProgram(
        name="kallisto",
        params=(
            Parameter(key="quant"),
            Parameter(key="--index", value=index),
            Parameter(key="--output-dir", value=output_dir),
        ),
        sample=sample,
        extra_flags=extra_flags,
    )

    input_files = [Parameter(key=str(fastq.path)) for fastq in sample.files.values()]

    for read in input_files:
        _kallisto.add_parameter(read)

    return _kallisto


def prokka_():
    """
    :return: Instance of PresetProgram containing Prokka.
    """
    _prokka = PresetProgram(name=Program("prokka"))  # no cover


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
        _prokka.add_parameter(param)

    if path.isdir(output_path):
        config.logger.warning(
            f"Warning: {output_path} directory exists. Will overwrite."
        )  # no cover
        _prokka.add_parameter(
            Parameter(key="--force", value="", kind="misc")
        )  # no cover

    # Add files according to their extension # TODO: add support for SeqFile
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
        Parameter(key="", value=str(_sample.files[assembly]), kind="input")
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
        kaiju_.add_parameter(p)

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
        kaiju2table_.add_parameter(p)

    # Add final parameter:
    kaiju2table_.cmd += f" {str(_sample.files[kaiju_output])}"

    if add_param_str:
        kaiju2table_.cmd += f" {add_param_str}"  # no cover

    return kaiju2table_
