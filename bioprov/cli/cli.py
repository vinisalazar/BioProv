"""
Module containing the class CLI and related functions.
"""
from bioprov.workflows import GenomeAnnotation


class WorkflowOptionsParser:
    """
    Class for parsing command-line options.
    """

    def __init__(self):
        pass

    @staticmethod
    def _genome_annotation(options):
        """
        Runs genome annotation workflow
        :return:
        """
        GenomeAnnotation.main(
            _input_path=options.input,
            labels=options.labels,
            files=options.files,
            _tag=options.tag,
            run_prokka=options.run_prokka,
            _skip_prodigal=options.skip_prodigal,
            _verbose=options.verbose,
            _threads=options.threads,
            _directory_input=options.directory,
        )

    def parse_options(self, options):
        """
        Parses options and returns correct workflow.
        :param options:
        :return:
        """
        if options.subparser_name == "genome_annotation":
            self._genome_annotation(options)
