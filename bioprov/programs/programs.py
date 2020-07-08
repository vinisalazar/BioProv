"""
Module for holding preset instances of the Program class.
"""

from bioprov import Program, Parameter


def prodigal(_sample):
    """
    Program Prodigal.
    :param _sample: Instance of BioProv Sample.
    :return:
    """
    file_preffix = str(_sample.files["assembly-file"]).replace(".fna", "")
    _sample.add_files(
        {
            "proteins": file_preffix + "_proteins.faa",
            "genes": file_preffix + "_genes.fna",
            "scores": file_preffix + "_score.cds",
        }
    )
    p = Program(
        "prodigal",
        params=(
            Parameter(key="-i", value=str(_sample.files["assembly"]), kind="input"),
            Parameter(key="-a", value=str(_sample.files["proteins"]), kind="output"),
            Parameter(key="-d", value=str(_sample.files["genes"]), kind="output"),
        ),
    )

    p.run(sample=_sample)
    if all(file_.exists for k, file_ in _sample.files.items()):
        return 0
