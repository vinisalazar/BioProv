## Changelog

### To-do
* Fix documentation issues [ ]
    * Add subpackage docstrings [ ]
* Add subparsers for CLI commands [ ]

### v0.1.17
* Add more database methods [ ]
* TBD [ ]

### v0.1.16
* Update README [x]
* Add Project.add_files() and add_programs() method [x]
* Improve Project deserializer [x]
* Add Project steps to Workflow class [x]

### v0.1.15
* Improve Sample.to_series() and Project.to_csv() methods [x]
* Add Project.to_csv() calls to tests [x]
* Add database commands to CLI options [x]
* Remodel environment as Agent rather than Entity [x]
* Improve output PROVN documents [x]
* Add Diamond preset and tests [x]

### v0.1.14
* Add blastdb example data [x]
* Add BLASTn preset and workflow and respective tests [x]
* Improve BioProvDB tests [x]
* Improve Project.auto_update and Project.sha1 behaviour and tests [x]
* Improve Workflow behaviour for custom Workflow arguments [x]

### v0.1.13
* Add BioProvDB class [x]
* Add database methods to Project class [x]
* Add BioProvDB tests [x]
* Add dot attribute to BioProvDocument [x]
* Update W3C-PROV tutorial [x]
* Improve test coverage [x]
* Debug Program deserializer [x]

### v0.1.12
* Patching errors for JSON IO [x]
    * Create File, Program, Run deserializers [x]
* Implement path replacing methods for multi-user support [x]

### v0.1.11
* Fix Run.start_time and Run.end_time testing [x]
* Improve Program tests [x]
* Allow users to have multiple environments [x]
* Improving internal PROV relationships [x]

### v0.1.10
* Refactoring hashes using hashlib [x]
* Removing EnvProv.env_set attribute [x]
* Implementing file hashes [x]
* Debug EnvProv JSON deserializer [x]
* Updating introductory tutorial [x]

### v0.1.9
* Improve Env constructor in Project deserializer [x]
* Improve Program behaviour when dealing with not found Programs [x]
* Implement utils.serializer_filter function [x]
* Improve pretty printing of commands [x]

### v0.1.8 
* Improve BioProvDocument constructor [x]
* Improve Sample and Program serializers [x]
* Improve internal PROV relationships [x]

### v0.1.7 
* Fix documentation build [x]
* Refactor f-strings [x]
* Draft of complete Prov document (all relationships) [x]

### v0.1.6
* Add more Provenance classes [x]
* Improve Provenance graph [x]
* Add contributing guidelines [x]
* Refactor config and prov modules [x]
* Add CLI options to show config [x]
* Rename src.program to src.main [x]
* Refactoring tests: joining src.program and src.sample tests into src.main [x]

### v0.1.5
* Add W3C-PROV tutorial [x]
* Small tweaks to default arguments in Program and File module [x]

### v0.1.4
* Fix PresetProgram.add_parameter bug [x]
* Add basic Tutorial [x]
* Refactor SeqStats data class [x]
* Improve Provenance classes [x]

### v0.1.3
* Patching more JSON IO bugs [x]

### v0.1.2
* Refactor functions in src.files module [x]
* Add support for BioPython AlignIO module [x]
* Patching src.program module [x]
* Improving JSON serializers [x]
