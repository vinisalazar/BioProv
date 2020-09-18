__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.2"

"""
Module containing base provenance attributes.

This module extracts system-level information, such as user and environment
settings, and stores them. It is invoked to export provenance objects. 
"""
from os import environ
from bioprov import Project
from bioprov.utils import Warnings
from prov.model import ProvDocument, Namespace, QualifiedName


class BioProvDocument:
    """
    Class containing base provenance information for a Prov ProvDocument.

    Adds two default namespaces: 'user', with present user and associated ProvAgent, and 'environment', with
    present environment variables and associated ProvEntity
    """

    def __init__(self, add_namespaces=True, _add_environ_attributes=True):
        """
        Constructor for the base provenance class.
        Creates a prov.model.ProvDocument instance and loads the main attributes.
        :param add_namespaces: Whether to add namespaces when initiating.
        """

        # Initialize ProvDocument
        self.ProvDocument = ProvDocument()
        self.env = EnvProv()
        self.user = self.env.user
        self.user_agent = None
        self.env_entity = None
        self.project = None
        self._add_environ_attributes = _add_environ_attributes

        if add_namespaces:
            self._add_namespaces()

    def _add_environ_namespace(self):
        self.ProvDocument.add_namespace(self.env.env_namespace)
        if self._add_environ_attributes:
            self.env_entity = self.ProvDocument.entity(
                "env:{}".format(self.env),
                other_attributes=build_prov_attributes(
                    self.env.env_dict, self.env.env_namespace
                ),
            )
        else:
            self.env_entity = self.ProvDocument.entity("env:{}".format(self.env),)

    def _add_user_namespace(self):
        self.ProvDocument.add_namespace("user", self.user)
        self.user_agent = self.ProvDocument.agent("user:{}".format(self.user))

    def _add_namespaces(self):
        self._add_environ_namespace()
        self._add_user_namespace()

    def _update_env(self):
        updated_env = self.env.update()
        self.env = updated_env


class BioProvProject(BioProvDocument):
    """
    Class containing base provenance information for a Project.
    """

    def __init__(self, project, **kwargs):
        """
        Constructs base provenance for a Project.
        :param project: Project being processed.
        :param kwargs: Keyword arguments to be passed to BioProvDocument.__init__().
        """
        # Inherit from BioProvDocument and add new attributes
        super().__init__(**kwargs)
        # Assert Project is good before constructing instance
        assert isinstance(project, Project), Warnings()["incorrect_type"](
            project, Project
        )
        self.project = project
        self.samples_entity = None
        self.activities = None

        # Updating attributes
        self._add_entities()
        self._add_samples()
        self._add_activities()
        self._add_relationships()

    def __repr__(self):
        return "BioProvProject describing Project '{}' with '{}' samples.".format(
            self.project.tag, len(self.project)
        )

    def _add_entities(self):
        self.ProvDocument.add_namespace("project", str(self.project))
        self.ProvDocument.add_namespace(
            "files",
            "Files associated with bioprov Project '{}'".format(self.project.tag),
        )
        self.project.entity = self.ProvDocument.entity(
            "project:{}".format(self.project)
        )
        # Check if project_csv exists
        if "project_csv" in self.project.files.keys():
            self.project_file_entity = self.ProvDocument.entity(
                "files:{}".format(self.project.files["project_csv"].path.name)
            )
        else:
            pass

    def _add_samples(self):

        self.ProvDocument.add_namespace(
            "samples",
            "Samples associated with bioprov Project '{}'".format(self.project.tag),
        )

        # Samples
        self.samples_entity = self.ProvDocument.entity(
            "samples:{}".format(str(self.project))
        )

    def _add_activities(self):

        self.ProvDocument.add_namespace(
            "activities",
            "Activities associated with bioprov Project '{}'".format(self.project.tag),
        )

        # Activities
        self.activities = {
            "import_Project": self.ProvDocument.activity(
                "activities:{}".format("bioprov.Project")
            ),
            "import_Sample": self.ProvDocument.activity(
                "activities:{}".format("bioprov.Sample")
            ),
        }

    def _add_relationships(self):
        # Relating project with user, project file, and sample
        # self.ProvDocument.wasAttributedTo(
        #     self.project.entity, "user:{}".format(self.user)
        # )
        for key, activity in self.activities.items():
            self.ProvDocument.wasAssociatedWith(activity, "user:{}".format(self.user))
        self.ProvDocument.wasGeneratedBy(
            self.project.entity, self.activities["import_Project"]
        )
        if self.project_file_entity is not None:
            self.ProvDocument.used(
                self.activities["import_Project"], self.project_file_entity
            )
        self.ProvDocument.used(self.activities["import_Sample"], self.project.entity)
        self.ProvDocument.wasGeneratedBy(
            self.samples_entity, self.activities["import_Sample"]
        )
        self.ProvDocument.wasAttributedTo(self.env_entity, self.user_agent)


class EnvProv:
    """
    Class containing provenance information about the current environment
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
        return "Environment_hash_{}".format(self.env_hash)

    def update(self):
        """
        Checks current environment and updates attributes using the os.environ module.
        :return: Sets attributes to self.
        """
        env_set = frozenset(environ.items())
        env_hash = hash(env_set)
        if env_hash != self.env_hash:
            self.env_set = env_set
            self.env_hash = env_hash
            self.env_dict = dict(self.env_set)
            self.user = self.env_dict["USER"]
            self.env_namespace = Namespace("env", str(self))


def build_prov_attributes(dictionary, namespace):
    """
    Inserting attributes into a Provenance object can be tricky. We need a NameSpace for said object,
    and attributes must be named correctly. This helper function builds a dictionary of attributes
    properly formatted to be inserted into a namespace

    :param dictionary: dict with object attributes
    :param namespace: instance of Namespace
    :return: List of tuples (QualifiedName, value)
    """

    # Check arg types
    assert isinstance(namespace, Namespace), Warnings()["incorrect_type"](
        namespace, Namespace
    )
    assert isinstance(dictionary, dict), Warnings()["incorrect_type"](dictionary, dict)

    attributes = []
    for k, v in dictionary.items():
        q = QualifiedName(namespace, str(k))
        attributes.append((q, v))

    return attributes
