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
it is increasingly important to properly manage computational analyses and data in order to
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
in web systems. We introduce BioProv as a library which aims to facilitate the creation of W3C-PROV compliant documents
for BWFs, capturing the provenance of the workflow steps between different users and computing environments.

# Statement of need

BioProv is a Python library for **generating provenance documents of bioinformatics workflows.**
Presently, there are excellent, freely available tools for orchestrating scientific workflows, such as Nextflow,
Snakemake and Toil [@Jackson2020], and others which specialize in capturing and storing provenance data during workflow runtime
[@Silva2018; @Khan2019]. However, to the best of our knowledge, there is not yet any library which specializes in capturing provenance of BWFs.
Some of these workflow management systems provide reports such as execution trace or graph, but they are not W3C-PROV compatible and/or
are not serializable, and the collection of domain specific information usually must be collected by the user in an *ad hoc* manner.
This can be very costly to both users and developers of BWFs looking to collect provenance data, as much effort can be spent
in modelling these workflows in a satisfactory data structure which can be easily updated during runtime [@DePaula2013]. BioProv attempts
to fill this gap, by providing features which facilitate the capture of W3C-PROV compatible provenance data and support the specificities of
bioinformatics applications.

# Features and data model

BioProv is **project-based**, and works by modelling the elements of a BWF in a hierarchical, JSON-serializable data structure.
Thus, BioProv objects can be easily stored and shared across computing environments, and can be exported as W3C-PROV compliant documents,
allowing better integration with web systems. BioProv implements five main classes (Table 1)

| Class   | Description                                                                                                                          | PROV element |
|---------|--------------------------------------------------------------------------------------------------------------------------------------|--------------|
| Project | Higher level structure which contains core project information. Contains associated samples, files, and programs.                    | Entity       |
| Sample  | Describes biological samples. Has attributes and contains associated files and programs.                                             | Entity       |
| File    | Describes computer files which may be associated with a Sample or Project (i.e. if it is associated with zero, two or more samples). | Entity       |
| Program | Describes programs which process and create files.                                                                                   | Activity     |


Lorem ipsum.

# Provenance documents

Lorem ipsum.

# Acknowledgements

We thank CNPq for funding scholarships for all authors.

# References