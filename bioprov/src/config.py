__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


"""
Contains the Config class and other package-level settings.
"""

import os
import bioprov
from bioprov.data import data_dir, genomes_dir
from prov.model import Namespace
from bioprov.utils import serializer, dict_to_sha1
from tinydb import TinyDB
from pathlib import Path


class Config:
    """
    Class to define package level variables and settings.
    """

    def __init__(self, db_path=None, threads=0):
        """
        :param db:
        :param threads:
        """
        # This duplication is to order the keys in the __dict__ attribute.
        self.user = None
        self.env = EnvProv()
        self.user = self.env.user
        if not threads:
            threads = str(int(os.cpu_count() / 2))
        self.db = None
        self.db_path = None
        self.threads = threads
        self.data = data_dir
        self.genomes = genomes_dir
        if db_path is None:
            db_path = Path(bioprov.__file__).parent.joinpath("db.json")
        self.db_path = db_path
        self.db = BioProvDB(self.db_path)

    def db_all(self):
        """
        :return: List all items in BioProv database.
        """
        return self.db.all()

    def clear_db(self, confirm=False):
        """
        Deletes the local BioProv database.
        :param confirm:
        :return:
        """
        self.db.clear_db(confirm)


class BioProvDB(TinyDB):
    """
    Inherits from tinydb.TinyDB

    Class to hold database configuration and methods.
    """

    def __init__(self, path):
        super().__init__(path)
        self.db_path = path

    def __repr__(self):
        return f"BioProvDB located in {self.db_path}"

    def clear_db(self, confirm=False):
        """
        Deletes the local BioProv database.
        :param confirm:
        :return:
        """
        proceed = True
        if not confirm:

            def _get_confirm():
                print(
                    f"The BioProv database at {self.db_path} containing {len(self)} projects will be erased."
                )
                print(
                    "This action cannot be reversed. Are you sure you want to proceed? y/N"
                )
                get_confirm = input()
                if get_confirm == "":
                    get_confirm = "n"
                if get_confirm.lower() in ("y", "yes"):
                    return True
                elif get_confirm.lower() in ("n", "no"):
                    return False
                else:
                    print("Invalid option. Please pick 'y' or 'n'.")
                    _get_confirm()

            proceed = _get_confirm()
        if proceed:
            self.truncate()
            print("Erased BioProv database.")
        else:
            print("Canceled operation.")


class EnvProv:
    """
    Class containing provenance information about the current environment.
    """

    def __init__(self):

        """
        Class constructor. All attributes are empty and are initialized with self.update()
        """
        self.env_hash = None
        self.env_dict = None
        self.user = None
        self.env_namespace = None
        self.update()

    def __repr__(self):
        return f"Environment_{self.env_hash}"

    def update(self):
        """
        Checks current environment and updates attributes using the os.environ module.
        :return: Sets attributes to self.
        """
        env_dict = dict(os.environ.items())
        env_hash = dict_to_sha1(env_dict)
        if env_hash != self.env_hash:
            self.env_dict = env_dict
            self.env_hash = env_hash

            # this is only to prevent build errors
            try:
                self.user = self.env_dict["USER"]
            except KeyError:  # no cover
                self.env_dict["USER"] = "unknown"  # no cover
            self.env_namespace = Namespace("env", str(self))

    def serializer(self):
        return serializer(self)


# Default config variable if not instantiating
config = Config()
