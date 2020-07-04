"""
Module containing the class CLI and related functions.
"""
import argparse


class CLI:
    """
    Class for holding bioprov's command-line application.
    """

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Run workflows and other tasks using BioProv.",
        )
        args = parser.parse_args()
        self.parser = parser
        self.args = args
        pass
