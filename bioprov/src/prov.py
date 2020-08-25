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
from coolname import generate_slug
from prov.model import ProvDocument


class BaseProvenance:
    """
    Class containing base provenance information.

    This includes system-level information and execution status
    """

    def __init__(self, default_namespace, project, workflow_name=None):
        """
        Constructor for the base provenance class.
        Defines main namespaces of the PROV object.
        The default namespace should be an URL linked with the analysis.
        For most purposes, we suggest this to be a GitHub repository,
        since it is mutable and has version control.

        :param default_namespace: URL linked to the analysis.
            Can be a GitHub repository
        :param workflow_name: Name of the workflow. If None, will be generated randomly.
        :param project: Project being processed.
        """

        # Get environment variables
        self.env = frozenset(environ.items())
        self.env_hash = hash(self.env)
        self.env_dict = dict(self.env)
        self.user = self.env_dict["USER"]

        # Start provenance document
        self.provdoc = ProvDocument()
        self.provdoc.add_namespace("user")

        # Default values to be set as namespaces
        default_values = {}

    pass
