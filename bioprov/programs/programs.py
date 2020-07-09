"""
Module for holding preset instances of the Program class.
"""

from bioprov import Program, Parameter


def prodigal(
    _sample, assembly="assembly", genes="genes", proteins="proteins", scores="scores",
):
    """
    :param _sample: An instance of BioProv Sample.
    :param assembly: Name of assembly file.
    :param genes: Name of genes file.
    :param proteins: Name of proteins file.
    :param scores: Name of scores file.
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
        prodigal_.add_parameter(param, _print=False)

    return prodigal_
