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
Presently, there are excellent, freely available tools for both orchestrating scientific workflows [@Koster2012; @DiTommaso2017] and
capturing and storing provenance data during workflow runtime [@Silva2018; @Khan2019].
However, to the best of our knowledge, there is not yet any library that specializes in capturing the provenance of BWFs.
Some of these workflow management systems provide reports such as execution trace or graph, but these reports are not W3C-PROV compatible and/or
are not serializable, and the collection of domain-specific information usually must be collected by the user with an *ad hoc* approach.
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

BioProv implements several classes (hereafter highlighted in bold text) in order to model BWFs. Its object-oriented design allows
users to enjoy the flexibility of working with extendable Python objects, which are familiar to many frameworks.
The four main classes are:

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
\label{fig:json}](figures/figure_1.png)

BioProv detects the current user and environment variables and stores them alongside the Project;
each Program, when run, is automatically associated with the current computing environment. This way, BioProv can represent which process
is associated with each user and environment, allowing for traceable collaborative work.

These four classes constitute the basis of a BioProv workflow. The library stores relevant metadata of each object:
for Samples, the attributes must be added upon data import, but for both Files and Programs, relevant information
is automatically captured, such as processes' start and end time and file size. 
Files containing biological sequences that are supported by BioPython can be parsed with the **SeqFile** class.
This class inherits from File and can extract metadata about the file contents, such as number of sequences,
number of base pairs, GC content (if it's a nucleotide file), and other metrics. This feature allows users to extract
domain data for their provenance reports by using all parsers available in BioPython.

Programs in BioProv can be created manually or loaded as a preset. We offer a few preset programs for common bioinformatics
tasks, such as sequence alignment search, multiple sequence alignment, gene prediction and quantification of gene expression. Some of the included programs are:

* **BLAST+:** sequence alignment search [@camacho2009blast]
* **Diamond:** sequence alignment search [@Buchfink2014]
* **MAFFT:** multiple sequence alignment [@Katoh2005]
* **Muscle:** multiple sequence alignment [@Edgar2004]
* **Prodigal:** prokaryotic gene prediction [@Hyatt2010]

Users can create their own presets with either the Program class or the **PresetProgram** class, which inherits from Program
and possesses additional methods for batch execution. To manually create programs (that are not presets), the user should
create the program as it is called from the command line, and add **Parameters** to it. A **Parameter** is another BioProv class
which represents specific parameters associated with a program. Presets will contain parameters specific to that program.
Parameters will be added to the program's command string which will be evaluated on the system's shell, by means of Python's
[`subprocess` module](https://docs.python.org/3/library/subprocess.html). For a more complete walkthrough of how to build programs
and add them to your workflow, please refer to the [tutorials](https://github.com/vinisalazar/BioProv/blob/master/docs/tutorials/introduction.ipynb).

## Importing and exporting data

There are a few ways to import and export data with BioProv. Here we present a few lines of code which produce an example
project to showcase this. If a project has not been previously imported, the most convenient way to import it is by
generating a table containing one sample per row, and columns with the path to each file associated with that sample.
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
                              sequencefile_cols="assembly",
                              tag="myProject",
                              import_data=True)
```

The table from which the data was sourced will automatically be added as a project file:

```
In [3]: project.files
Out[3]: {'project_csv': /home/user/myProject/myTable.csv}
```

And Samples will be created with associated files and attributes:

```
In [4]: project["sample_1"]
Out[4]: Sample sample_1 with 2 file(s).

In [5]: project["sample_1"].files
Out[5]: 
{'report': /home/user/myProject/report_1.txt,
 'assembly': /home/user/myProject/contigs_1.fasta}

In [6]: project["sample_1"].attributes                                                                                                                                                                           
Out[6]: {'source': 'seawater'}
```

Sequence metadata is extracted from sequence files, as set by the `import_data=True` parameter:

```
In [7]: project["sample_1"].files["assembly"].GC                                                                                                                                                                
Out[7]: 0.36442
```

To run a program using BioProv, it must be added to the project or to a sample. We can use the preset `prodigal` program
to illustrate this. Prodigal runs a gene prediction algorithm for prokaryotic genomes, and creates three output files:

Now that their project is loaded, the user can add new files, samples and programs. Programs can be run and execution provenance
will be captured (such as **stdout** and **stderr**, start and end time, and files involved).

```
In [8]: from bioprov.programs import prodigal                                                                                                                                                                                              

In [9]: with project["sample_1"] as sample: 
            sample.add_programs(prodigal(sample))
            sample.run_programs()
```

To export the project, there are a few options. The user can either:

   * export the project in a tabular format such as the one presented in `myTable.csv`. This will omit project information (about programs, for example),
   but will preserve information of samples and files. Done with the `Project.to_csv()` method;
   * export the project as JSON, the preferred option, as BioProv can deserialize this format back into a `Project` object with all related information; Done with
   the `Project.to_json()` method;
   * store the project in BioProv's database. BioProv has a builtin document-oriented database, as explained in the following section.

```
In [10]: project.to_csv()  # exports in tabular format

In [11]: project.to_json()  # exports as JSON

In [12]: project.update_db()  # stores in the BioProv database
Inserting new project 'myProject' in /path/to/bioprov/db.json                                                                                                                                                   
```

## Database system
BioProv implements an internal database using [TinyDB](https://tinydb.readthedocs.io/en/latest/), a document-oriented, pure
Python database. Projects can be easily loaded by their ID (the `Project.tag` attribute) and can be updated during runtime, by
setting the `Project.auto_update = True` option. Assuming the user has run the previous code example, this could be done in a 
new session:

```
In [1]: import bioprov as bp

In [2]: project = bp.load_project("myProject")  # call projects by their tag

In [3]: project.auto_update = True
``` 

Now all future modifications to `myProject` will auto-update its record in BioProv's database. 
The database can be managed from BioProv's CLI application.

## Command line application and workflows

To use the CLI, after installing, simply type `bioprov`:

```
~/ $ bioprov
usage: bioprov [-h]
               [--show_config | --show_provstore | --create_provstore |
                --show_db | --clear_db | -v | -l]
               {genome_annotation,blastn,kaiju} ...

BioProv command-line application. Choose a command to begin.

optional arguments:
  -h, --help            show this help message and exit
  --show_config         Show location of config file.
  --show_provstore      Show location of ProvStore credentials file.
  --create_provstore    Create ProvStore credentials file.
  --show_db             Show location of database file.
  --clear_db            Clears all records in database.
  -v, --version         Show BioProv version
  -l, --list            List Projects in the BioProv database.

workflows:
  {genome_annotation,blastn,kaiju}
```

The `bioprov --show_db` and `bioprov --list` commands, for example, can be used to show the location of BioProv's
database and list all projects it contains. The `workflows` are preset pipelines that can be run directly from the CLI.
They are implemented with BioProv's **Workflow** class and handle the creation of the BioProv project while
running the desired pipeline. A user can write their own **Workflow** and the command-line parser will be automatically generated
based on the parameters set by the user. For more information, please refer to BioProv's 
[`workflows` subpackage](https://github.com/vinisalazar/BioProv/tree/master/bioprov/workflows), where preset workflows are stored, or run 
the `bioprov <workflow_name>` command in the CLI for help about a particular workflow. Presently, BioProv workflows are still 
limited, serving mainly as a reference for users to write their own workflows. However, one of the main future goals of the library is to
support a range of common BWFs. We actively encourage users to contribute their workflows by following the 
[contributing guidelines](https://github.com/vinisalazar/BioProv/blob/master/CONTRIBUTING.md) or request one by opening an issue in the repository.

# Provenance documents

To create W3C-PROV documents, BioProv utilizes the PROV library [@Dong2020], and models its native objects onto
the three PROV elements: **entities**, **agents**, and **activities** (@Groth2013 provide a detailed description of the PROV ontology).
To do this, a **Project** is imported with the **BioProvDocument** class. A W3C-PROV compatible document will be created, with
associated relationships between PROV elements for each object of the project. BioProv defines one "bundle" for the project, and one 
for each sample and user. Bundles are documents nested within the top-level **BioProvDocument**, used to describe individual entities (for the Sample bundles)
or agents (for the user bundles). Computing environments are also agents, which **act on behalf of** users through **activities**
(which correspond to BioProv's **Programs**). By leveraging the PROV library, the resulting document can be exported in a number of ways, such as 
graphical format and [PROV-N](https://www.w3.org/TR/prov-n/) (a human-readable provenance format).

The following code will generate the \autoref{fig:project} and a PROV-N record:

```
In [4]: prov = bp.BioProvDocument(project, add_users=False)

In [5]: prov.write_provn()

In [6]: prov.dot.write_pdf("myProject.pdf")
```

![Provenance graph created by BioProv with the PROV and PyDot libraries. This graph represents a Project containing a single
sample associated with a bacterial genome. The `prodigal` program uses the `assembly` file as input to create the `proteins`
file.\label{fig:project}](figures/figure_2.png)

Lastly, **BioProvDocuments** can be uploaded to [ProvStore](https://openprovenance.org/store/), a web service for storage and visualization
of W3C-PROV documents. The credentials to the ProvStore API are set with the `bioprov --create_provstore` command, and a document can be
uploaded with the `upload_to_provstore()` method:

```
In [7]: prov.upload_to_provstore()
```

This feature enables the immediate publication of provenance documents that have a uniform resource identifier (URI)
through their ProvStore address. Future developments for further supporting the W3C-PROV standard in the field of bioinformatics
should focus on integrating more web services, such as [NCBI Entrez](https://www.ncbi.nlm.nih.gov/Web/Search/entrezfs.html) and
[Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page), for continuous improvement of the reproducibility of BWFs.

# Conclusion

We present a software library that allows users to create and run bioinformatics workflows while capturing provenance data
during runtime, which can then be exported as a W3C-PROV compliant document. Provenance data can be easily imported and exported in
widely-used and web-compatible formats, and users can collect domain-specific data in a fast and effortless manner. BioProv is written
entirely in Python and its objects can be extended and customized to suit users' needs. This results in a complete library that
can quickly make any computational project more provenance-aware, setting BioProv as a valuable addition to the ecosystem of
bioinformatics workflow tools.

# Acknowledgements

We thank CNPq for funding scholarships for all authors.

# References
