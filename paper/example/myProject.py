import bioprov as bp

project = bp.read_csv(
    "myTable.csv",
    file_cols="report",
    sequencefile_cols="assembly",
    tag="myProject",
    import_data=True,
)

project.files

project["sample_1"]

project["sample_1"].files

project["sample_1"].attributes

project["sample_1"].files["assembly"].GC

del project["sample_2"]

from bioprov.programs import prodigal

with project["sample_1"] as sample:
    sample.add_programs(prodigal(sample))
    sample.run_programs()

project.to_csv()  # exports in tabular format

project.to_json()  # exports as JSON

project.update_db()

project = bp.load_project("myProject")  # call projects by their tag

project.auto_update = True

prov = bp.BioProvDocument(project, add_users=False)

prov.write_provn()

prov.dot.write_pdf("myProject_nousers.pdf")
