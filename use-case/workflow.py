#!/usr/bin/env python
# coding: utf-8

import argparse
import bioprov as bp
from bioprov.programs import prodigal


# preprocessing
def download(input_file):

    metadata = input_file.replace(".txt", "_metadata.txt")

    _download = bp.Program("ncbi-genome-download")

    params = [
        bp.Parameter("-F", "fasta,assembly-report"),
        bp.Parameter("-s", "genbank"),
        bp.Parameter("-A", input_file),
        bp.Parameter("-o", "data/"),
        bp.Parameter("-m", metadata),
        bp.Parameter("bacteria"),
    ]

    for param in params:
        _download.add_parameter(param)

    _download.run(suppress_stderr=False)

    return _download, metadata


def sort(metadata):

    _sort = bp.Program("sort")

    params = [
        bp.Parameter("-t", "' '"),
        bp.Parameter("-k", "1,1"),
        bp.Parameter("-u", metadata),
        bp.Parameter("-r"),
        bp.Parameter("-o", metadata),
    ]

    for param in params:
        _sort.add_parameter(param)

    _sort.run(suppress_stderr=False)

    return _sort


def gunzip():
    _gunzip = bp.Program("gunzip")
    _gunzip.add_parameter(bp.Parameter("-f", "data/genbank/bacteria/*/*"))
    _gunzip.run(suppress_stderr=False)
    return _gunzip


def sed_gz(metadata):
    _sed_gz = bp.Program("sed_gz")
    _sed_gz.found = True
    params = [
        bp.Parameter("sed"),
        bp.Parameter("-i"),
        bp.Parameter("'s/.gz//g'"),
        bp.Parameter(metadata),
    ]

    for param in params:
        _sed_gz.add_parameter(param)
    _sed_gz.run(suppress_stderr=False)

    return _sed_gz


def sed_column(metadata):
    _sed_column = bp.Program("sed_column")
    _sed_column.found = True
    params = [
        bp.Parameter("sed"),
        bp.Parameter("-i"),
        bp.Parameter("'s/local_filename/genome_assembly/g'"),
        bp.Parameter(str(metadata)),
    ]

    for param in params:
        _sed_column.add_parameter(param)

    _sed_column.run(suppress_stderr=False)

    return _sed_column


def load_project(tag, metadata, programs):
    proj = bp.read_csv(
        metadata,
        sep="\t",
        sequencefile_cols="genome_assembly",
        import_data=True,
        tag=tag,
    )

    proj.add_programs(programs)
    proj.update_db()
    proj.auto_update = True
    proj.start_logging(f"data/{proj.tag}.log")

    return proj


# processing

# gene calling
def prodigal_(proj):
    for sample in proj:
        p = prodigal(input_tag="genome_assembly")
        del p.output_files["-s"]
        p.create_func(sample)
        sample.add_programs(p)
        sample.run_programs()


# pairwise gene comparison
def fastani(proj):
    fastani_input = bp.File(f"data/fastani_input_{proj.tag}.txt", tag="fastani_input")
    fastani_output = bp.File(
        f"data/fastani_output_{proj.tag}.txt", tag="fastani_output"
    )
    proj.add_files(fastani_input)
    proj.add_files(fastani_output)
    with open(proj.files["fastani_input"].path, "w") as f:
        for file in (sample.files["genome_assembly"] for sample in proj):
            f.write(str(file) + "\n")

    _fastani = bp.Program("fastANI")

    params = [
        bp.Parameter("--refList", proj.files["fastani_input"], kind="input"),
        bp.Parameter("--queryList", proj.files["fastani_input"]),
        bp.Parameter("--threads", bp.config.threads),
        bp.Parameter("--fragLen", 200),
        bp.Parameter("--minFraction", 0.01),
        bp.Parameter("--output", proj.files["fastani_output"], kind="output"),
    ]

    for param in params:
        _fastani.add_parameter(param)

    proj.add_programs(_fastani)
    _fastani.run(suppress_stderr=False)


# format output
def format_fastani_output(proj):
    ffo_f = bp.File("data/fastani_output_fmt.txt")
    proj.add_files(ffo_f)

    ffo_p = bp.Program("format_fastani_output")
    ffo_p.found = True

    params = [
        bp.Parameter("python", "format_fastani_output.py"),
        bp.Parameter("-i", proj.files["fastani_output"], kind="input"),
        bp.Parameter("-o", proj.files["fastani_output_fmt"], kind="output"),
        bp.Parameter("--invert"),
    ]

    for param in params:
        ffo_p.add_parameter(param)

    proj.add_programs(ffo_p)
    ffo_p.run(suppress_stderr=False)


# create labels
def labels(proj):
    _labels = bp.File(f"data/labels_{proj.tag}.txt", tag="labels")
    proj.add_files(_labels)
    with open(_labels.path, "w") as f:
        for sample in proj:
            filename = str(sample.files["genome_assembly"].basename)
            label = sample.attributes["organism_name"]
            f.write(f"{filename},{label}\n")


# cluster and plot
def cluster(proj):
    dendrogram = bp.File(f"data/dendrogram_{proj.tag}.pdf", tag="dendrogram")
    proj.add_files(dendrogram)

    clust = bp.Program("cluster_and_plot")
    clust.found = True

    params = [
        bp.Parameter("python", "hierarchical_clustering.py"),
        bp.Parameter("-t", proj.files["fastani_output_fmt"], kind="input"),
        bp.Parameter("-l", proj.files["labels"], kind="misc"),
        bp.Parameter("-o", proj.files["dendrogram"], kind="output"),
        bp.Parameter("-c", 22.5, kind="misc"),
        bp.Parameter("-s", "10,6", kind="misc"),
    ]

    for param in params:
        clust.add_parameter(param)

    proj.add_programs(clust)
    clust.run(suppress_stderr=False)


def export_provenance(proj):
    prov = bp.BioProvDocument(proj)
    prov.dot.write_pdf(f"graphs/{proj.tag}.pdf")
    prov.write_provn(f"data/{proj.tag}_provn.txt")


def preprocessing(input_file, tag):
    _download, metadata = download(input_file)
    _sort = sort(metadata)
    _gunzip = gunzip()
    _sed_gz = sed_gz(metadata)
    _sed_column = sed_column(metadata)
    load_project(tag, metadata, [_download, _sort, _gunzip, _sed_gz, _sed_column])


def processing(tag):
    proj = bp.load_project(tag)
    proj.auto_update = True
    prodigal_(proj)
    fastani(proj)
    format_fastani_output(proj)
    labels(proj)
    cluster(proj)
    export_provenance(proj)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BioProv use case with a genomic taxonomy workflow."
    )
    parser.add_argument(
        "-i", "--input-file", help="Input file with one accession number per line."
    )
    parser.add_argument("-t", "--tag", help="Project tag.")
    parser.add_argument(
        "-s",
        "--skip-preprocessing",
        help="Whether to skip the preprocessing step.",
        action="store_true",
    )
    _args = parser.parse_args()

    if not _args.skip_preprocessing:
        preprocessing(_args.input_file, _args.tag)

    processing(_args.tag)
