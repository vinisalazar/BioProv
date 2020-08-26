__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"

"""
Module containing base provenance attributes.

This module extracts system-level information, such as user and environment
settings, and stores them. It is invoked to export provenance objects. 
"""
from os import environ
from bioprov import Project
from bioprov.utils import warnings
from prov.model import ProvDocument


class BaseProvenance:
    """
    Class containing base provenance information.

    This includes system-level information and execution status
    """

    def __init__(self, project):
        """
        Constructor for the base provenance class.
        Creates a prov.model.ProvDocument instance and
        loads the main attributes.
        :param project: Project being processed.
        """

        # Get environment variables
        self.env = frozenset(environ.items())
        self.env_hash = hash(self.env)
        self.env_dict = dict(self.env)
        self.user = self.env_dict["USER"]

        # Set Project
        assert isinstance(project, Project), warnings["incorrect_type"](
            project, Project
        )
        self.project = project

        # Start provenance document
        self.provdoc = ProvDocument()
        self.provdoc.add_namespace("user", self.user)
        self.provdoc.add_namespace("project", self.project.tag)
        self.provdoc.add_namespace("samples", str(project))
        self.provdoc.add_namespace(
            "files", "Files associated with project '{}'".format(project.tag)
        )
        self.provdoc.add_namespace(
            "activities", "Activities associated with project '{}'".format(project.tag)
        )

        # Add user agent
        self.provdoc.agent("user:{}".format(self.user))

        # Add project entity
        self.project.entity = self.provdoc.entity("project:{}".format(project.tag))
        self.project_file = self.provdoc.entity(
            "project:{}".format(self.project.files["project_csv"])
        )

    pass
