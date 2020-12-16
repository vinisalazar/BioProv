__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"

"""
Module containing base provenance attributes.

This module extracts system-level information, such as user and environment
settings, and stores them. It is invoked to export provenance objects. 
"""
import logging
from pathlib import Path

from prov.dot import prov_to_dot
from prov.model import ProvDocument
from requests.exceptions import ConnectionError

from bioprov import Project, Parameter, config
from bioprov.utils import Warnings, build_prov_attributes, serializer_filter


class BioProvDocument:
    """
    Class containing base provenance information for a Project.
    """

    def __init__(
        self,
        project,
        add_attributes=False,
        add_users=True,
        _add_project_namespaces=True,
        _iter_samples=True,
        _iter_project=True,
    ):
        """
        Constructs the W3C-PROV document for a project.

        :param Project project: instance of bioprov.src.Project.
        :param bool add_attributes: whether to add object attributes.
        :param bool add_users: whether to add users and environments.
        :param bool _add_project_namespaces:
        :param bool _iter_samples:
        :param bool _iter_project:
        """

        # Assert Project is good before constructing instance
        assert isinstance(project, Project), Warnings()["incorrect_type"](
            project, Project
        )
        self.ProvDocument = ProvDocument()
        self.project = project
        self.project.document = self.ProvDocument
        self._dot = prov_to_dot(self.ProvDocument)
        self._provn = self.ProvDocument.get_provn()
        self._entities = dict()
        self._activities = dict()
        self._agents = dict()
        self._user_bundles = dict()
        self._provstore_document = None

        # Don't add attributes if you plan on exporting to graphic format
        self.add_attributes = add_attributes

        # Set this before running Namespaces
        if add_users:
            self._create_envs_and_users = True

        else:
            self._create_envs_and_users = False

        # Default actions to create the document
        if _add_project_namespaces:
            self._add_project_namespaces()

        if self._create_envs_and_users:
            self._iter_envs_and_users()

        if _iter_project:
            self._iter_project()

        if _iter_samples:
            self._iter_samples()

    def __repr__(self):
        return "BioProvDocument describing Project '{}' with {} samples.".format(
            self.project.tag, len(self.project)
        )

    @property
    def dot(self):
        self._dot = prov_to_dot(self.ProvDocument)
        return self._dot

    @dot.setter
    def dot(self, value):
        self._dot = value

    @property
    def provn(self):
        self._provn = self.ProvDocument.get_provn()
        return self._provn

    @provn.setter
    def provn(self, value):
        self._provn = value

    @property
    def provstore_document(self):
        self._provstore_document = self.ProvDocument
        return self._provstore_document

    @provstore_document.setter
    def provstore_document(self, value):
        self._provstore_document = value

    def _add_project_namespaces(self):
        """
        Runs the three _add_namespace functions.
        :return:
        """
        self._add_project_namespace()
        if self._create_envs_and_users:
            self._add_env_and_user_namespace()
        self._add_samples_namespace()
        self._add_activities_namespace()

    def _add_project_namespace(self):
        """
        Creates the Project Namespace and Project Entity.
        # Sets the default Namespace of the BioProvDocument as the Project.

        :return: updates self.project and self.ProvDocument.
        """
        self.ProvDocument.add_namespace("project", str(self.project))

    def _add_env_and_user_namespace(self):
        self.ProvDocument.add_namespace(
            "users", f"Users associated with BioProv Project '{self.project.tag}'"
        )

    def _add_samples_namespace(self):
        self.ProvDocument.add_namespace(
            "samples",
            f"Samples associated with bioprov Project '{self.project.tag}'",
        )

    def _add_files_namespace(self):
        self.ProvDocument.add_namespace(
            "files", f"Files associated with bioprov Project '{self.project.tag}'"
        )

    def _iter_project(self):
        self._create_sample_bundle(self.project, kind="Project")
        self._create_sample_file_entities(self.project, kind="Project")
        self._create_program_entities(self.project, kind="Project")

    def _iter_envs_and_users(self):
        for _user, _env_dict in self.project.users.items():
            _user_preffix = f"users:{_user}"
            _user_bundle = self._user_bundles[_user] = self.ProvDocument.bundle(
                _user_preffix
            )
            _user_bundle.set_default_namespace(_user)
            _user_bundle.add_namespace(
                "envs", f"Environments associated with User '{_user}'"
            )
            self._agents[_user] = _user_bundle.agent(_user_preffix)

    def _iter_samples(self):
        for _, sample in self.project.samples.items():
            for statement in (
                self._create_sample_bundle(sample),
                self._create_sample_file_entities(sample),
                self._create_program_entities(sample),
            ):
                try:
                    statement
                except KeyError:
                    config.logger.debug(
                        f"Could not run function '{statement.__name__}' for sample {sample.name}."
                    )
                    pass

    def _create_sample_bundle(self, object_, kind="Sample"):
        """
        Creates a ProvBundle for the Sample and associates it to self.ProvDocument.

        :param object_: instance of bioprov.Sample
        :return: updates self.ProvDocument by creating PROV objects for the sample.
        """
        choices = ("Sample", "Project")
        assert kind in choices, Warnings()["choices"](kind, choices, "kind")
        # Sample PROV attributes: bundle, namespace, entity
        object_.ProvBundle = self.ProvDocument.bundle(object_.namespace_preffix)
        object_.ProvBundle.set_default_namespace(object_.name)
        self._entities[object_.name] = object_.entity = object_.ProvBundle.entity(
            object_.namespace_preffix
        )
        if kind == "Sample":
            object_.ProvBundle.wasDerivedFrom(
                self._entities[object_.name], self.project.entity
            )

    def _create_sample_file_entities(self, sample, kind="Sample"):
        """
        Creates a ProvBundle for the Sample and associates it to self.ProvDocument.

        :param sample: instance of bioprov.Sample
        :return: updates the sample.ProvBundle by creating PROV objects for the files.

        """
        sample.files_namespace_preffix = "files"
        sample.file_namespace = sample.ProvBundle.add_namespace(
            sample.files_namespace_preffix,
            f"Files associated with {kind} {sample.name}",
        )
        # Files PROV attributes: namespace, entities
        for key, file in sample.files.items():
            # This prevents errors when the file refers to a project csv or JSON
            if file.name == sample.name:
                file.name = file.basename
            # Same function call, but in the first we pass the 'other_attributes' argument
            if self.add_attributes:
                self._entities[file.name] = sample.ProvBundle.entity(
                    f"{sample.files_namespace_preffix}:{file.tag}",
                    other_attributes=build_prov_attributes(
                        file.serializer(), sample.file_namespace
                    ),
                )
            else:
                self._entities[file.name] = sample.ProvBundle.entity(
                    f"{sample.files_namespace_preffix}:{file.tag}",
                )

            # Adding relationships
            sample.ProvBundle.wasDerivedFrom(
                self._entities[file.name],
                self._entities[sample.name],
            )

    def _create_program_entities(self, sample, kind="Sample"):
        # Programs PROV attributes: namespace, entities
        programs_namespace_prefix = f"programs"
        programs_namespace = sample.ProvBundle.add_namespace(
            programs_namespace_prefix,
            f"Programs associated with {kind} {sample.name}",
        )
        for key, program in sample.programs.items():
            last_run = program.runs[str(len(program.runs))]

            # We want to exclude _runs from the program serializer
            # So we put a custom serializer filter
            keys = ("sample", "_runs")
            serialized_program = serializer_filter(program, keys)
            try:
                del serialized_program["params"]
            except KeyError:
                pass

            # Same function call, but in the first we pass the 'other_attributes' argument
            if self.add_attributes:
                self._activities[program.name] = sample.ProvBundle.activity(
                    f"{programs_namespace_prefix}:{program.name}",
                    startTime=last_run.start_time,
                    endTime=last_run.end_time,
                    other_attributes=build_prov_attributes(
                        serialized_program, programs_namespace
                    ),
                )
            else:
                self._activities[program.name] = sample.ProvBundle.activity(
                    f"{programs_namespace_prefix}:{program.name}",
                    startTime=last_run.start_time,
                    endTime=last_run.end_time,
                )

            if self._create_envs_and_users:
                for _user, _env_dict in self.project.users.items():
                    _user_bundle = self._user_bundles[_user]
                    for _env_hash, _env in _env_dict.items():
                        if _env_hash == last_run.env:
                            if self.add_attributes:
                                self._agents[_env_hash] = _user_bundle.agent(
                                    f"envs:{_env}",
                                    other_attributes=build_prov_attributes(
                                        _env.env_dict, _env.env_namespace
                                    ),
                                )
                            else:
                                self._agents[_env_hash] = _user_bundle.agent(
                                    f"envs:{_env}"
                                )
                            _user_bundle.actedOnBehalfOf(
                                self._agents[_env_hash], self._agents[_user]
                            )
                sample.ProvBundle.wasAssociatedWith(
                    self._activities[program.name], self._agents[last_run.env]
                )

            inputs, outputs = self._get_IO_from_params(program)
            self._add_IO_relationships(sample, program, inputs, "input")
            self._add_IO_relationships(sample, program, outputs, "output")

    def _add_IO_relationships(self, sample, program, io_list, io_type):
        # TODO: replace Sample for Project when implementing Project.files and programs

        """
        Add PROV relationships between Program and input/output files.

        :param sample: instance of bioprov.Sample
        :param program: instance of bioprov.Program
        :param io_list: list of input/output files
        :param io_type: 'input' or 'output'
        :return: Adds relationship between
        """

        # Small assertion block
        choices = ("input", "output")
        assert io_type in choices, Warnings()["choices"](io_type, choices, "io_type")

        # Start function
        sample_files = [str(file) for _, file in sample.files.items()]
        for value in io_list:
            if value in sample_files:
                file_obj = [
                    file_ for _, file_ in sample.files.items() if str(file_) == value
                ]
                if file_obj:
                    file_obj, *_ = file_obj
                    if io_type == "input":
                        sample.ProvBundle.used(
                            self._entities[file_obj.name],
                            self._activities[program.name],
                        )
                    elif io_type == "output":
                        sample.ProvBundle.wasGeneratedBy(
                            self._entities[file_obj.name],
                            self._activities[program.name],
                        )

    @staticmethod
    def _get_IO_from_params(program):
        """
        :param program: instance of bioprov.Program
        :return: list of input parameter values and list of output parameter values
        """
        # Relationships based on Parameters
        inputs, outputs = [], []

        for _, parameter in program.params.items():
            assert isinstance(parameter, Parameter), (
                Warnings()["incorrect_type"](parameter, Parameter)
                + "\nPlease check if Programs were correctly deserialized."
            )
            if parameter.kind == "input":
                # This loop is because some positional arguments may have empty values (value stored in parameter.key)
                if parameter.value:
                    inputs.append(parameter.value)
                else:
                    inputs.append(parameter.key)
            elif parameter.kind == "output":
                if parameter.value:
                    outputs.append(parameter.value)
                else:
                    outputs.append(parameter.key)

        return inputs, outputs

    def _add_activities_namespace(self):
        """
        Add activities Namespace to self.
        :return:
        """

        if len(self.ProvDocument.namespaces) == 0:
            self.ProvDocument.add_namespace(
                "activities",
                f"Activities associated with bioprov Project '{self.project.tag}'",
            )

    def upload_to_provstore(self, api=None):
        """
        Uploads self.ProvDocument. to ProvStore (https://openprovenance.org/store/)

        :param api: provstore.api.Api
        :return: Sends POST request to ProvStore API and updates self.ProvDocument if successful.
        """
        if api is None:
            api = config.provstore_api
        try:
            self.provstore_document = api.document.create(
                self.ProvDocument, name=self.project.tag
            )
        except ConnectionError:
            logging.error(
                "Could not create remote document. Please check your internet connection and ProvStore credentials."
            )

    def write_provn(self, path=None):
        """
        Writes PROVN output of document.
        :param path: Path to write file.
        :return: Writes file.
        """
        if path is None:
            path = f"./{self.project.tag}_provn"
            if self.add_attributes:
                path += "_attrs"
            path += ".txt"

        path = Path(path)
        assert (
            path.parent.exists()
        ), f"Directory '{path.parent}' not found.\nPlease provide a valid directory."

        if path.exists():
            logging.info(f"Overwriting file at '{path}'")

        with open(path, "w") as f:
            f.write(self.provn)
            if path.exists():
                logging.info(f"Wrote PROVN record to {path}.")
