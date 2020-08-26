### BioProv - provenance capturing for bioinformatics.

[![Build Status](https://travis-ci.org/vinisalazar/BioProv.svg?branch=master)](https://travis-ci.org/vinisalazar/BioProv)
[![Coverage Status](https://coveralls.io/repos/github/vinisalazar/BioProv/badge.svg?branch=master&service=github)](https://coveralls.io/github/vinisalazar/BioProv?branch=master&service=github)
[![License](https://img.shields.io/github/license/vinisalazar/bioprov)](https://img.shields.io/github/license/vinisalazar/bioprov)
[![Requirements Status](https://requires.io/github/vinisalazar/BioProv/requirements.svg?branch=master)](https://requires.io/github/vinisalazar/BioProv/requirements/?branch=master)

BioProv is a Python library for builiding bioinformatics pipelines and easily extracting provenance data.

```bibtex
>>> import bioprov as bp

# Create samples and file objects
>>> sample = bp.Sample("mysample")
>>> genome = bp.SequenceFile("mysample.fasta", "genome")
>>> sample.add_files(genome)

# Create programs
>>> output = sample.files["blast_out"] = bp.File("mysample.blast.tsv", "blast_out")
>>> blast = bp.Program("blastn", params={"-query": sample.files["genome"], "-db": "mydb.fasta", "-out": output})

# Run programs
>>> blast.run(sample=sample)  # Or sample.run(program=blast)
```

BioProv is built with the [Biopython](https://biopython.org/) and [Pandas](http://pandas.pydata.org/) libraries.

You can import data into BioProv using Pandas objects.

```bibtex
# Read csv straight into BioProv
>>> samples = bp.read_csv("my_dataframe.tsv", sep="\t", sequencefile_cols="assembly")

# Alternatively, use a pandas DataFrame
>>> df = pd.read_csv("my_dataframe.tsv", sep="\t")

# [...] manipulate your df
>>> df["assembly"] = "assembly_directory/" + df["assembly"]

# Now load from your df
>>> samples = bp.from_df(df, sequencefile_cols="assembly")

# `samples` becomes a Project dict-like object
>>> sample1 = samples['sample1']
```

BioProv 'SequenceFile' objects contains records formatted as [BioPython SeqRecords](https://biopython.org/wiki/SeqRecord):

```bibtex
>>> type(sample1)
Bio.SeqRecord.SeqRecord
```

BioProv objects can be imported or exported as JSON objects.

```bibtex
>>> sample1.to_json(), samples.to_json()
```


### Installation

```bibtex
$ git clone https://github.com/vinisalazar/bioprov  # download
$ cd bioprov; pip install .                         # install
$ pytest                                            # test
```

Contributions are welcome!

**BioProv is in active development and no warranties are provided (please see the License).**
