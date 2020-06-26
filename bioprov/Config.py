"""
Contains the Config class.
"""
from .data import data_dir, genomes_dir


class Config:
    """
    Class to define package level variables and settings.
    """

    def __init__(self):
        self.data_dir = data_dir
        self.genomes_dir = genomes_dir

    pass


config = Config()
