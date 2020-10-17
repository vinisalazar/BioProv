__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.8"


"""
Contains the Config class.
"""
import os
from bioprov.data import data_dir, genomes_dir
from prov.model import Namespace
from bioprov.utils import build_prov_attributes, serializer


class Config:
    """
    Class to define package level variables and settings.
    """

    def __init__(self, threads=0):
        # This duplication is to order the keys in the __dict__ attribute.
        self.user = None
        self.env = EnvProv()
        self.user = self.env.user
        if not threads:
            threads = str(int(os.cpu_count() / 2))
        self.threads = threads
        self.data = data_dir
        self.genomes = genomes_dir

    pass


class EnvProv:
    """
    Class containing provenance information about the current environment.
    """

    def __init__(self):

        """
        Class constructor. All attributes are empty and are initialized with self.update()
        """
        self.env_set = None
        self.env_hash = None
        self.env_dict = None
        self.user = None
        self.env_namespace = None
        self.update()

    def __repr__(self):
        return f"Environment_hash_{self.env_hash}"

    def update(self):
        """
        Checks current environment and updates attributes using the os.environ module.
        :return: Sets attributes to self.
        """
        env_set = frozenset(os.environ.items())
        env_hash = hash(env_set)
        if env_hash != self.env_hash:
            self.env_set = env_set
            self.env_hash = env_hash
            self.env_dict = dict(self.env_set)

            # this is only to prevent build errors
            try:
                self.user = self.env_dict["USER"]
            except KeyError:
                self.env_dict["USER"] = "unknown"
            self.env_namespace = Namespace("env", str(self))

    def _build_prov_attributes(self):
        """
        Adds self.env_dict to self.env_namespace.
        """
        return build_prov_attributes(self.env_dict, self.env_namespace)

    def serializer(self):
        return serializer(self)


# Default config variable if not instantiating
config = Config()
