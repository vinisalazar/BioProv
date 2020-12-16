__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


"""
Contains the Config class and other package-level settings.

Define your configurations in the 'config' variable at the end of the module.
"""

import os
from pathlib import Path

from prov.model import Namespace
from provstore.api import Api
from tinydb import TinyDB

from bioprov import __file__ as bp_file
from bioprov.data import data_dir, genomes_dir
from bioprov.utils import serializer, dict_to_sha1, serializer_filter, create_logger


class Config:
    """
    Class to define package level variables and settings.
    """

    def __init__(self, db_path=None, threads=0):
        """
        :param db_path: Path to database file. Default is bioprov_directory/db.json
        :param threads: Number of threads. Default is half of processors.
        """
        # This duplication is to order the keys in the __dict__ attribute.
        self.user = None
        self.env = Environment()
        self.user = self.env.user
        if not threads:
            threads = int(os.cpu_count() / 2)
        self.db = None
        self.db_path = None
        self.threads = threads
        self.bioprov_dir = Path(bp_file).parent
        self.data = data_dir
        self.genomes = genomes_dir
        if db_path is None:
            db_path = self.bioprov_dir.joinpath("db.json")
        self.db_path = db_path
        self.db = BioProvDB(self.db_path)
        self._provstore_file = None
        self._provstore_user = None
        self._provstore_token = None
        self._provstore_api = None
        self._provstore_endpoint = "https://openprovenance.org/store/api/v0/"
        self._logger = None

    def __repr__(self):
        return f"BioProv Config class set in {__file__}"

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
        self.db.clear_db(confirm)  # no cover

    @property
    def provstore_api(self):
        if self._provstore_api is None:
            self._provstore_api = Api(
                username=self.provstore_user, api_key=self.provstore_token
            )
            self._provstore_api.base_url = self._provstore_endpoint
        return self._provstore_api

    @provstore_api.setter
    def provstore_api(self, value):
        self._provstore_api = value

    @property
    def provstore_file(self):
        if self._provstore_file is None:
            self._provstore_file = self.bioprov_dir.joinpath("provstore_api.txt")
        return self._provstore_file

    @provstore_file.setter
    def provstore_file(self, value):
        self._provstore_file = value

    @property
    def provstore_user(self):  # no cover
        if self._provstore_user is None:
            self.read_provstore_file()
        return self._provstore_user

    @provstore_user.setter
    def provstore_user(self, value):
        self._provstore_user = value

    @property
    def provstore_token(self):  # no cover
        if self._provstore_token is None:
            self.read_provstore_file()
        return self._provstore_token

    @provstore_token.setter
    def provstore_token(self, value):
        self._provstore_token = value

    @property
    def logger(self):
        if self._logger is None:
            self._logger = create_logger()
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    def create_provstore_file(self, user=None, token=None):  # no cover
        with open(self.provstore_file, "w") as f:
            if user is None:
                user = input("Please paste your ProvStore user: ")
            if token is None:
                token = input("Please paste your ProvStore API token: ")
            f.write(user + "\n")
            f.write(token + "\n")

        print(f"Wrote ProvStore credentials file to {self.provstore_file}.")
        print("Make sure that the contents of that file are private.")

    def read_provstore_file(self):
        """
        Attempts to read self.provstore_file.
        Will prompt to create one if unable to retrieve credentials.

        :return: Updates self.provstore_user and self.provstore_token.
        """
        could_not_read = [
            f"Could not read credentials from ProvStore file at {self.provstore_file}",
            "It may be empty or not exist.",
        ]

        def prompt():  # no cover
            _prompt = input(
                "\n".join(could_not_read + ["Would you like to create one? Y/n\n"])
            )
            if _prompt.lower() in ("y", "yes", ""):
                return True
            else:
                print("Did not create ProvStore credentials file.")
                return False

        try:
            with open(self.provstore_file) as f:
                user, token, *_ = f.read().splitlines()
                assert all((user, token))
                self.provstore_user = user
                self.provstore_token = token
                return

        # If not found, prompt to create
        except FileNotFoundError:  # no cover
            if prompt():
                self.create_provstore_file()
                self.read_provstore_file()
            else:
                return

        # Any other errors, return None and raise Exception
        except (ValueError, AssertionError, UnboundLocalError):  # no cover
            print(
                "\n".join(
                    could_not_read
                    + [
                        "Please create one with bioprov.config.create_provstore_file() method."
                    ]
                )
            )
            self.provstore_user = None
            self.provstore_token = None
            return

    def serializer(self):
        keys_to_remove = [i for i in self.__dict__.keys() if i.startswith("_")] + [
            "env",
        ]
        serial_out = serializer_filter(self, keys_to_remove)
        serial_out["provstore_file"] = self.provstore_file
        return serial_out


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

    def clear_db(self, confirm=False):  # no cover
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


class Environment:
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
        return self.env_hash

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
            self.env_namespace = Namespace("envs", str(self))

    def serializer(self):
        return serializer(self)


config = Config()
