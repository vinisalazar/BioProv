## Changelog

### To-do
* [ ] Fix documentation issues
    * [ ] Add subpackage docstrings
* [ ] Create methods for Sample and Pro
    * [ ] .describe
    * [ ] .write_paths_to_file, .copy_files_to_dir(), .link_files_to_dir()
    * [ ] .total_duration
* [ ] Add logger calls when saving to JSON and uploading to ProvStore

### v0.1.24
* [x] State requirements more clearly
* [x] Improve error handling when getting `Program` attributes
* [x] Add `__doc__` variable to modules to build documentation
* [x] Fix `File.size` property
* [x] Add `File.raw_size` property

### v0.1.23
* [x] Patch PresetProgram SeqFile addition feature
* [x] Fix SeqFile deserializer
* [x] Add import_records arg to `bp.load_project()`
* [x] Improve reserved aminoacid characters
* [x] Add `SeqFile.max_seq` and `.min_seq` properties
* [x] Patch `Project` deserializer to improve BioProvDocument creation
* [x] Make shorter Environment hashes
* [x] Improve Project `__repr__`

### v0.1.22
* [x] Simplify `bp.load_project()` function
* [x] Fix user and env PROV relationships
* [x] Add Run attributes as Program class properties (will consume from the last run)
* [x] Add sequence dunder methods for Project class
* [x] Improve run methods
* [x] Allow specifying sequence format to PresetProgram outputs
* [x] Update env file to Py 3.9

### v0.1.21
* [x] Add _config argument to `bp.load_project()` (this is a temporary fix)
* [x] Add db property to Config class (prevents bug when setting DB path)
* [x] Improve a few docstrings
* [x] Refactor sha1 as sha256   
* [x] Add add and radd dunder methods for Directory and File  
* [x] Package workflows in single module
* [x] Add FastTree PresetProgram

### v0.1.20
* [x] Debug graphical DOT output
* [x] Add Muscle PresetProgram
* [x] Add MAFFT PresetProgram
* [x] Add Kallisto PresetProgram
* [x] Add extra_flags attribute to PresetProgram
* [x] Refactor EnvProv class as Environment
* [x] Allow creation of users and envs to be optional
* [x] Create environments only when there's an associated activity
* [x] Create Sample dunder enter and dunder exit methods
* [x] Fixing wasDerivedFrom bug when sample and file have same names
* [x] Fix extra Environments bug

### v0.1.19
* [x] Debug API endpoint (#23)
* [x] Implement logging
    * [x] Implement Workflow logging
* [x] Debug Workflow Steps
* [x] Remove workflow main methods
    * [x] Workflows must now be called only from the CLI
* [x] Implement post-workflow actions
    * [x] Update db
    * [x] Upload to ProvStore
    * [x] Write PROVN
    * [x] Write PDF
* [x] Add Sample.auto_update_db() methods
* [x] Remove logger call when updating Project in database

### v0.1.18a
* [x] Patch file deserializer bug

### v0.1.18
* [x] Add support for ProvStore API (#23)
* [x] Add subparsers for CLI commands
* [x] Add Directories class to Files module
    * [x] Support globbing Directory outputs
* [x] Increase test coverage
* [x] Added more example data
* [x] Make config.threads an integer to support operations

### v0.1.17
* [x] Add more database methods
* [x] Improver error handling for JSON methods
* [x] Add Project.run_programs method
* [x] Create ProvEntity and ProvActivity for Project.files and .programs
    * [x] Create Project Bundle for .files and .programs

### v0.1.16
* [x] Update README
* [x] Add Project.add_files() and add_programs() method
* [x] Improve Project deserializer
* [x] Add Project steps to Workflow class

### v0.1.15
* [x] Improve Sample.to_series() and Project.to_csv() methods
* [x] Add Project.to_csv() calls to tests
* [x] Add database commands to CLI options
* [x] Remodel environment as Agent rather than Entity
* [x] Improve output PROVN documents
* [x] Add Diamond preset and tests

### v0.1.14
* [x] Add blastdb example data
* [x] Add BLASTn preset and workflow and respective tests
* [x] Improve BioProvDB tests
* [x] Improve Project.auto_update and Project.sha1 behaviour and tests
* [x] Improve Workflow behaviour for custom Workflow arguments

### v0.1.13
* [x] Add BioProvDB class
* [x] Add database methods to Project class
* [x] Add BioProvDB tests
* [x] Add dot attribute to BioProvDocument
* [x] Update W3C-PROV tutorial
* [x] Improve test coverage
* [x] Debug Program deserializer

### v0.1.12
* [x] Patching errors for JSON IO
    * [x] Create File, Program, Run deserializers
* [x] Implement path replacing methods for multi-user support

### v0.1.11
* [x] Fix Run.start_time and Run.end_time testing
* [x] Improve Program tests
* [x] Allow users to have multiple environments
* [x] Improving internal PROV relationships

### v0.1.10
* [x] Refactoring hashes using hashlib
* [x] Removing EnvProv.env_set attribute
* [x] Implementing file hashes
* [x] Debug EnvProv JSON deserializer
* [x] Updating introductory tutorial

### v0.1.9
* [x] Improve Env constructor in Project deserializer
* [x] Improve Program behaviour when dealing with not found Programs
* [x] Implement utils.serializer_filter function
* [x] Improve pretty printing of commands

### v0.1.8 
* [x] Improve BioProvDocument constructor
* [x] Improve Sample and Program serializers
* [x] Improve internal PROV relationships

### v0.1.7 
* [x] Fix documentation build
* [x] Refactor f-strings
* [x] Draft of complete Prov document (all relationships)

### v0.1.6
* [x] Add more Provenance classes
* [x] Improve Provenance graph
* [x] Add contributing guidelines
* [x] Refactor config and prov modules
* [x] Add CLI options to show config
* [x] Rename src.program to src.main
* [x] Refactoring tests: joining src.program and src.sample tests into src.main

### v0.1.5
* [x] Add W3C-PROV tutorial
* [x] Small tweaks to default arguments in Program and File module

### v0.1.4
* [x] Fix PresetProgram.add_parameter bug
* [x] Add basic Tutorial
* [x] Refactor SeqStats data class
* [x] Improve Provenance classes

### v0.1.3
* [x] Patching more JSON IO bugs

### v0.1.2
* [x] Refactor functions in src.files module
* [x] Add support for BioPython AlignIO module
* [x] Patching src.program module
* [x] Improving JSON serializers
