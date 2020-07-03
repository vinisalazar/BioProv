### BioProv - provenance capturing for bioinformatics.

BioProv is a Python library for builiding bioinformatics pipelines and easily extracting provenance data.

```bibtex
import bioprov as bp

# Create samples and file objects
sample = bp.Sample("mysample")
genome = bp.SequenceFile("mysample.fasta", "genome")
sample.add_files(genome)

# Create programs
blast = bp.Program("blastn", params={"-query": sample.files["genome"], "-db": "mydb.fasta"})

# Run programs
blast.run(sample=sample)  # Or
sample.run(program=blast)
```