---
title: 'BioProv - provenance documents for bioinformatics workflows'
tags:
 - Python
 - W3C-PROV
 - BioPython
 - pipelines
 - reproducibility
 - PROV
 - JSON
authors:
 - name: Vinícius W. Salazar^[Corresponding author]
   orcid: 0000-0002-8362-3195
   affiliation: 1
 - name: João Vitor Ferreira Cavalcante
   orcid: 0000-0001-7513-7376
   affiliation: 2
 - name: Fabiano Thompson
   orcid: 0000-0002-7562-1683
   affiliation: 3
 - name: Marta Mattoso
   orcid: 0000-0002-0870-3371
   affiliation: 1
affiliations:
 - name: Department of Systems and Computer Engineering, COPPE, Federal University of Rio de Janeiro
   index: 1
 - name: Bioinformatics Multidisciplinary Environment—BioME, IMD, Federal University of Rio Grande do Norte
   index: 2
 - name: Institute of Biology, Federal University of Rio de Janeiro
   index: 3
date: 1 January 2020
bibliography: paper.bib
---

# Summary

In an era where it can be argued that all biology is computational biology [@Markowetz2017],
it is increasingly important to properly manage computational analyses and data to
ensure the reproducibility of *in silico* experiments. A major aspect of best practices in 
scientific computing [@wilson2017good] is managing the **provenance** of data. The World Wide Web
Consortium (W3C) Provenance Working Group defines provenance as ["a record that describes the people,
institutions, entities, and activities involved in producing, influencing, or delivering a piece of 
data or a thing"](https://www.w3.org/TR/prov-overview/) [@Groth2013]. 

Therefore, for bioinformatics workflows (BWFs), where there are usually numerous, and many times complex,
steps in data processing, capturing and storing provenance rapidly becomes a challenge.
This provenance data should not only be intelligible to humans, but structured and machine-readable; 
this is fundamental to ensure reproducibility in present and future research in bioinformatics and
many other fields of scientific research [@Kanwal2017; @Pasquier2017]. A proposed standard for interoperability of provenance
data is the [W3C-PROV data model](https://www.w3.org/TR/prov-dm/), specifically designed to share provenance data
across the web. However, modelling BWFs with the W3C-PROV standard can be costly to both 
researchers writing and performing the analyses and developers responsible for storing information about these workflows
in web systems. We introduce BioProv as a library that aims to facilitate the creation of W3C-PROV compliant documents
for BWFs, capturing the provenance of the workflow steps between different users and computing environments.

# Statement of need

BioProv is a Python library for **generating provenance documents of bioinformatics workflows.**
Presently, there are excellent, freely available tools for orchestrating scientific workflows, such as Nextflow,
Snakemake, and Toil [@Jackson2020], and others that focus in capturing and storing provenance data during workflow runtime
[@Silva2018; @Khan2019]. However, to the best of our knowledge, there is not yet any library that specializes in capturing the provenance of BWFs.
Some of these workflow management systems provide reports such as execution trace or graph, but these reports are not W3C-PROV compatible and/or
are not serializable, and the collection of domain-specific information usually must be collected by the user in an *ad hoc* manner.
This can be very costly to both users and developers of BWFs looking to collect provenance data, as much effort can be spent
in modelling these workflows in a satisfactory data structure that can be easily updated during runtime [@DePaula2013]. BioProv attempts
to fill this gap, by providing features that allow capturing W3C-PROV compatible provenance data and support the specificities of
bioinformatics applications.

# Features and data model

## Overview

BioProv is **object-oriented** and **project-based**. It works by modelling the provenance elements of a BWF in a hierarchical, JSON-serializable data structure
Thus, BioProv objects can be easily stored and shared across computing environments, and can be exported as W3C-PROV compliant documents,
allowing better integration with web systems. It can be used interactively, in an environment such as Jupyter [@ragan2014jupyter],
or from the command line (CLI), as it can be used to quickly write provenance-aware workflows that can be launched using
the `bioprov <workflow_name>` command. BioProv uses the BioPython [@Cock2009] library as a wrapper to parse bioinformatics file formats, as it supports
several file formats for both [sequence](https://biopython.org/wiki/SeqIO) and [alignment](https://biopython.org/wiki/AlignIO) data, allowing the user
to easily extract domain data without having to write any parsers. Here we present some of the core features of BioProv, but for a more complete introduction,
we recommend the package's [tutorials](https://github.com/vinisalazar/BioProv/blob/master/docs/tutorials/introduction.ipynb) in Jupyter Notebook format, that
can also be launched [via Binder](https://mybinder.org/v2/gh/vinisalazar/bioprov/master?filepath=docs%2Ftutorials%2F), and the [documentation page](https://bioprov.readthedocs.io/).
For example data, we provide five small bacterial genomes and a BLAST database that is a subset of MEGARES [@Lakin2017]. These two datasets can 
be used to test the installation and illustrate some of the core features of BioProv.

## Classes

BioProv implements four main classes:

* **Project:** The higher-level structure that contains core project information. Contains associated samples, files, and programs.
* **Sample:** Describes biological samples. Has attributes and contains associated files and programs.
* **File:** Describes computer files that may be associated with a Sample or Project (i.e. if it is associated with zero, two, or more samples).
* **Program:** Describes programs that process and create files.
<!-- * **Workflow:** Describes a sequence of programs that are run on project- or sample-level files. Used mostly with the CLI functionality. -->

A **Project** will be the top-level object in a BioProv workflow. It will contain $n$ biological **Samples** that may have
individually associated **Files** (for example, raw sequence data in FASTQ format) and **Programs**, which are processes that can be run
to create and/or modify files. Files and Programs can also be associated directly with the Project, instead of being associated with a 
particular Sample (\autoref{fig:json}).

![The BioProv data model follows an hierarchical, JSON-serializable structure. This example is adapted for illustrative purposes.
\label{fig:json}](figures/json.png)

BioProv detects the current user and environment variables and stores them alongside the Project;
each Program, when run, is automatically associated with the current computing environment. This way, BioProv can represent which process
is associated with each user and environment, allowing for traceable collaborative work.

These four classes constitute the basis of a BioProv workflow. The library stores relevant metadata of each object:
for Samples, the attributes must be added upon data import, but for both Files and Programs, relevant information
is automatically captured, such as processes' start and end time and file size. 
Files containing biological sequences that are supported by BioPython can be parsed with the **SeqFile** class.
This class inherits from File and can extract metadata about the file contents, such as number of sequences,
number of base pairs, GC content (if it's a nucleotide file), and other metrics. This feature allows users to extract
domain data for their provenance reports by leveraging the available parsers in BioPython.

<!-- Mention Workflows, PresetPrograms here -->

## IO and database system

There are a few ways to import and export data with BioProv. If a project has not been previously imported, the most convenient
way to import it is by generating a table containing one sample per row, and columns with the path to each file associated with that sample.
Columns that are not files will be processed as sample attributes. For example, assume the following table:

| sample-id 	| assembly        	| report       	| source   	|
|-----------	|-----------------	|--------------	|----------	|
| sample_1  	| contigs_1.fasta 	| report_1.txt 	| seawater 	|
| sample_2  	| contigs_2.fasta 	| report_2.txt 	| soil     	|

The `sample-id` column will be our index, each sample will be identified by it. It is a good practice to make this the first column
in the table. The `assembly` column contains the path to the genome assembly of each sample (therefore, a "sequence file").
The `report` column points to a plain text file contaning the assembly report (therefore, a "file").
The other columns will be parsed as sample attributes. This can be easily done with the `read_csv()` function:

```
In [1]: import bioprov as bp

In [2]: project = bp.read_csv("myTable.csv",
                      file_cols="report",
                      sequencefile_cols="assembly"
                      tag="myProject",
                      import_data=True)
```

The table from which the data was source will automatically be added as a project file:

```
In [3]: project.files
Out[3]: {'project_csv': /home/user/myProject/myTable.csv}
```

And Samples will be created with associated files and attributes:

```
In [4]: project['sample_1']
Out[4]: Sample sample_1 with 2 file(s).

In [5]: project['sample_1'].files
Out[5]: 
{'report': /Users/vini/Bio/BioProv/paper/example/report_1.txt,
 'assembly': /Users/vini/Bio/BioProv/paper/example/contigs_1.fasta}

In [6]: project['sample_1'].attributes                                                                                                                                                                           
Out[6]: {'source': 'seawater'}
```

Sequence metadata is extracted from sequence files, as set by the `import_data=True` parameter:

```
In [7]: project['sample_1'].files['assembly'].GC                                                                                                                                                                
Out[7]: 0.36442
```


# Provenance documents

Lorem ipsum. This is a reference to \autoref{fig:project}.

![Provenance graph created by BioProv with the PROV and PyDot libraries. This graph represents a Project containing a single
sample associated with a cyanobacterial genome. The `prodigal` program uses the `assembly` file as input to create the `proteins` file.\label{fig:project}](figures/project.png)

# Acknowledgements

We thank CNPq for funding scholarships for all authors.

# References