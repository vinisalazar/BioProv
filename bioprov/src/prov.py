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


class ProjectProv:
    """
    Class containing base provenance information for a Project.
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

        # Agents
        self.provdoc.agent("user:{}".format(self.user))

        # Entities
        self.project.entity = self.provdoc.entity("project:{}".format(project.tag))

        try:
            self.project_file_entity = self.provdoc.entity(
                "files:{}".format(self.project.files["project_csv"].path.name)
            )
        except KeyError:
            raise Exception(
                "No 'project_csv' file associated with Project '{}'. Please create a project CSV file.".format(
                    self.project.tag
                )
            )
        self.samples_entity = self.provdoc.entity("samples:{}".format(str(project)))

        # Activities
        self.activities = {
            "import_Project": self.provdoc.activity(
                "activities:{}".format("bioprov.Project")
            ),
            "import_Sample": self.provdoc.activity(
                "activities:{}".format("bioprov.Sample")
            ),
        }

        # Relating project with user, project file, and sample
        self.provdoc.wasAttributedTo(self.project.entity, "user:{}".format(self.user))
        self.provdoc.wasGeneratedBy(
            self.project.entity, self.activities["import_Project"]
        )
        self.provdoc.used(self.activities["import_Project"], self.project_file_entity)
        self.provdoc.used(self.activities["import_Sample"], self.project.entity)
        self.provdoc.wasGeneratedBy(
            self.samples_entity, self.activities["import_Sample"]
        )
