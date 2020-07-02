"""
Testing for the Sample module.
"""
from bioprov.Sample import Sample
from bioprov.data import synechococcus_genome


def test_Sample():
    """
    Testing for the Sample class.
    :return:
    """
    attributes = {
        "name": "GCF_000010065.1_ASM1006v1",
        "tag": "Synechococcus elongatus PCC 6301",
        "files": dict(),
        "attributes": {"habitat": "freshwater"},
    }
    s = Sample()
    for attr, v in attributes.items():
        setattr(s, attr, v)
        assert getattr(s, attr) == v

    assembly_path = synechococcus_genome
    s.add_files({"assembly": assembly_path})
    s.add_files({"proteins": assembly_path.replace(".fna", ".faa")})
    assert s.files["assembly"].exists, f"Couldn't find file in path {assembly_path}."
