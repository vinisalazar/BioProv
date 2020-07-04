"""
Module containing the class CLI and related functions.
"""
import argparse
import sys


class CLI:
    """
    Class for holding bioprov's command-line application.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="BioProv command-line application.",
            description="Run workflows and other tasks using BioProv.",
        )
        pass
