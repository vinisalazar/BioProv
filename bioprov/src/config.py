__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


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
            self.threads = str(int(os.cpu_count() / 2))

    pass


# Default config variable if not instantiating
default_config = Config()
