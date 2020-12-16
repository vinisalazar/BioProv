__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


"""
Module containing the Workflow options parser for preset workflows.
"""


from bioprov.workflows import genome_annotation, blastn_alignment, KaijuWorkflow


class WorkflowOptionsParser:
    """
    Class for parsing command-line options.
    """

    def __init__(self):
        pass

    @staticmethod
    def _blastn_alignment(kwargs, steps):
        """
        Runs blastn alignment workflow
        :return:
        """
        main = blastn_alignment(**kwargs)
        main.run_steps(steps)

    @staticmethod
    def _genome_annotation(kwargs, steps):
        """
        Runs genome annotation workflow
        :return:
        """
        main = genome_annotation(**kwargs)
        main.run_steps(steps)

    @staticmethod
    def _kaiju_workflow(kwargs, steps):
        """
        Runs Kaiju workflow
        :return:
        """
        _ = steps
        KaijuWorkflow.main(**kwargs)

    def parse_options(self, options):
        """
        Parses options and returns correct workflow.
        :type options: argparse.Namespace
        :param options: arguments passed by the parser.
        :return: Runs the specified subparser in options.subparser_name.
        """
        subparsers = {
            "genome_annotation": lambda _options, _steps: self._genome_annotation(
                _options, _steps
            ),
            "blastn": lambda _options, _steps: self._blastn_alignment(_options, _steps),
            "kaiju": lambda _options, _steps: self._kaiju_workflow(_options, _steps),
        }

        # Run desired subparser
        kwargs = dict(options._get_kwargs())
        steps = kwargs.pop("steps")
        subparsers[options.subparser_name](kwargs, steps)
