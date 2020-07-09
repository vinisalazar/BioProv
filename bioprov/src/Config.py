"""
Contains the Config class.
"""
import os
from bioprov.data import data_dir, genomes_dir


class Config:
    """
    Class to define package level variables and settings.
    """

    def __init__(self, threads=0):
        self.data_dir = data_dir
        self.genomes_dir = genomes_dir
        if not threads:  # By default, use half of processors.
            self.threads = int(os.cpu_count() / 2)

    pass


# Default config variable if not instantiating
config = Config()
