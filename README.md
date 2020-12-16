### BioProv - W3C-PROV provenance documents for bioinformatics


Package | [![License](https://img.shields.io/github/license/vinisalazar/bioprov)](https://github.com/vinisalazar/BioProv/blob/master/LICENSE) | [![PyPI Version](https://img.shields.io/pypi/v/bioprov)](https://pypi.org/project/bioprov/) | [![Requirements Status](https://requires.io/github/vinisalazar/BioProv/requirements.svg?branch=master)](https://requires.io/github/vinisalazar/BioProv/requirements/?branch=master)
---------------|--|--|--
Tests | [![Build Status](https://travis-ci.org/vinisalazar/BioProv.svg?branch=master)](https://travis-ci.org/vinisalazar/BioProv) |  [![tests](https://github.com/vinisalazar/bioprov/workflows/tests/badge.svg?branch=master)](https://github.com/vinisalazar/bioprov/actions?query=workflow%3Atests) | [![Coverage Status](https://coveralls.io/repos/github/vinisalazar/BioProv/badge.svg?branch=master&service=github)](https://coveralls.io/github/vinisalazar/BioProv?branch=master&service=github)
Code | [![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) | [![lint](https://github.com/vinisalazar/BioProv/workflows/lint/badge.svg?branch=master)](https://github.com/vinisalazar/BioProv/actions?query=workflow%3Alint)
Docs | [![Docs status](https://readthedocs.org/projects/bioprov/badge/?version=latest)](https://bioprov.readthedocs.io/en/latest/?badge=latest) | [![binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/vinisalazar/bioprov/master?filepath=docs%2Ftutorials%2F)


BioProv is a Python library for [W3C-PROV](https://www.w3.org/TR/prov-overview/) representation of bioinformatics workflows.
 It enables you to quickly write workflows and to describe relationships between samples, files, users and programs.

Please see the [tutorials](./docs/tutorials/introduction.ipynb) for a more detailed introduction and
 visit [ReadTheDocs](https://bioprov.readthedocs.io/) for the complete documentation.

### Quickstart

```py
>>> import bioprov as bp

# Create samples and file objects
>>> sample = bp.Sample("mysample")
>>> genome = bp.File("mysample.fasta", "genome")
>>> sample.add_files(genome)

# Create programs
>>> output = sample.files["blast_out"] = bp.File("mysample.blast.tsv", "blast_out")
>>> blastn = bp.Program("blastn",
                        params={"-query": sample.files["genome"],
                                "-db": "mydb.fasta", "-out": output}
                        )
>>> sample.add_programs(blastn)

# Run programs
>>> sample.run_programs()

# Save your project
>>> proj = bp.Project((sample,), tag="example_project")
>>> proj.to_json()

# Create PROV documents
>>> prov = bp.BioProvDocument(proj)

# Save in PROVN or graphical format
>>> prov.write_provn()  # human-readable text format
>>> prov.dot.write_pdf()  # graphical format
```

BioProv also has a command-line application to run preset workflows.

```
$ bioprov -h
usage: bioprov [-h] [--show_config | --show_db | --clear_db | -v | -l]
               {genome_annotation,blastn,kaiju} ...

BioProv command-line application. Choose a command to begin.

optional arguments:
  -h, --help            show this help message and exit
  --show_config         Show location of config file.
  --show_db             Show location of database file.
  --clear_db            Clears all records in database.
  -v, --version         Show BioProv version
  -l, --list            List Projects in the BioProv database.

workflows:
  {genome_annotation,blastn,kaiju}

```

BioProv is built with the [Biopython](https://biopython.org/) and [Pandas](http://pandas.pydata.org/) libraries.

You can import data into BioProv using Pandas objects.

```py
# Read csv straight into BioProv
>>> samples = bp.read_csv("my_dataframe.tsv", sep="\t", sequencefile_cols="assembly")

# Alternatively, use a pandas DataFrame
>>> df = pd.read_csv("my_dataframe.tsv", sep="\t")

# [...] manipulate your df
>>> df["assembly"] = "assembly_directory/" + df["assembly"]

# Now load from your df
>>> project = bp.from_df(df, sequencefile_cols="assembly", source_file="my_dataframe.tsv")

# `samples` becomes a Project dict-like object
>>> sample1 = project['sample1']

# You can also export your sample and associated files and attributes as a dataframe
>>> project.to_csv()
```

### Installation

```sh
# Install from pip
$ pip install bioprov

# Or install from source
$ git clone https://github.com/vinisalazar/bioprov  # download
$ cd bioprov; pip install .                         # install
$ pytest                                            # test
```

**Important!** BioProv requires [Prodigal](https://github.com/hyattpd/Prodigal) to be tested. Otherwise tests will fail.

Contributions are welcome!

**BioProv is in active development and no warranties are provided (please see the License).**
