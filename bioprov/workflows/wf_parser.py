__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Module containing the Workflow options parser for preset workflows.
"""


from bioprov.workflows import genome_annotation, KaijuWorkflow


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
        main = genome_annotation()
        main.input = options.input
        steps = options.steps
        main.run_steps(steps)

    @staticmethod
    def _kaiju_workflow(options):
        """
        Runs Kaiju workflow
        :return:
        """
        KaijuWorkflow.main(
            input_file=options.input,
            output_path=options.output_directory,
            kaijudb=options.kaiju_db,
            nodes=options.nodes,
            names=options.names,
            threads=options.threads,
            _tag=options.tag,
            verbose=options.verbose,
            kaiju_params=options.kaiju_params,
            kaiju2table_params=options.kaiju2table_params,
        )

    def parse_options(self, options):
        """
        Parses options and returns correct workflow.
        :param options:
        :return:
        """
        subparsers = {
            "genome_annotation": lambda _options: self._genome_annotation(_options),
            "kaiju": lambda _options: self._kaiju_workflow(_options),
        }

        # Run desired subparser
        subparsers[options.subparser_name](options)
