---
title: 'BioProv: W3C-PROV representation of biological data structures and workflows'
tags:
  - Python
  - bioinformatics
  - provenance
  - W3C-PROV
  - workflows
  - reproducibility
  - documents
authors:
  - name: Vinícius Werneck Salazar^[Corresponding author.]
    orcid: 0000-0002-8362-3195
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Fabiano Lopes Thompson
    affiliation: 2
  - name: Marta Mattoso
    affiliation: 1
affiliations:
 - name: Department of Systems Engineering and Computer Science, COPPE,
         Federal University of Rio de Janeiro
   index: 1
 - name: Institute of Biology, Federal University of Rio de Janeiro.
   index: 2
date: 21 September 2020
bibliography: paper.bib
---

# Summary

The development and implementation of bioinformatics workflows (BWFs) is a common activity in life sciences research.
Despite the wide availability of tools to manage scientific workflows [@cite], the formal representation of
 BWFs remains a challenge. A particurlarly important aspect of any scientific workflow representation
 is the description of an object's *provenance* [@cite], which documents its computational origins, and promotes
 the reproducibility of the workflow which processes or generates said object.
 
Although there are examples of the formal representation of provenance in BWFs, the provenance extraction of domain 
 specific (biological) data needs to either be implemented by hand, or by using a generic provenance extraction tool 
 (e.g. [@cite]), both of which can be quite labourious. Provenance extraction can also be integrated with each platform
 (e.g. [@cite qiime2]), but this limits workflows combining several programs.
 
In order to improve this, we present BioProv, a Python library for the provenance representation of biological
 data structures and workflows. BioProv implements the W3C-PROV-DM model and JSON serializers, to ensure a standard
 format across documents and compatibility with document-oriented databases and external REST APIs, such as the
 ProvStore web service [@cite].
  
BioProv is designed to be project-based and agnostic to the mode of execution of each workflow, which means that BioProv code
can be integrated into the scripts of third-party execution services, such as Nextflow or Snakemake, while still capturing
runtime provenance data, allowing for maximum flexibility. It can also be used interactively in notebook environments such
as Jupyter Notebook or RMarkdown.

# Statement of need 

To the best of our knowledge, there is yet no framework for the W3C-PROV representation of BWFs or biological data structures.
Enabling users to quickly write and implement BWFs which are provenance-aware applications can dramatically improve - and facilitate -
 the reproducibility of said workflows, and allow the exchange of standardized artifacts which accurately
 describe these workflows. The JSON compatibility of BioProv's objects also implicate that they are suitable to be transmitted via
 HTTP requests, which has useful applications for web services.

# Examples

Lorem ipsum.

# Key references

Lorem ipsum.

# Publications

BioProv was initially motivated by two projects that analysed public NCBI Genbank data to investigate the genomic taxonomy
of the *Prochlorococcus* and *Synechococcus* collectives, respectively. These efforts were subsequently published at
 [@cite], [@cite].
Although the publications do not cite BioProv (due to the library being in early developmental stages),
the library's prototype greatly assisted data analysis.

# Acknowledgements

Lorem ipsum.

# References

