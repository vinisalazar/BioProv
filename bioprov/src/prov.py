__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"

"""
Module containing base provenance attributes.

This module extracts system-level information, such as user and environment
settings, and stores them. It is invoked to export provenance objects. 
"""
from bioprov import Project, Parameter
from bioprov.utils import Warnings, build_prov_attributes, serializer_filter
from prov.model import ProvDocument
from prov.dot import prov_to_dot


class BioProvDocument:
    """
    Class containing base provenance information for a Project.
    """

    def __init__(
        self,
        project,
        add_attributes=False,
        _add_project_namespaces=True,
        _iter_envs_and_users=True,
        _iter_samples=True,
    ):
        """
        Constructs base provenance for a Project.
        :param project: Project being processed.
        """

        # Assert Project is good before constructing instance
        assert isinstance(project, Project), Warnings()["incorrect_type"](
            project, Project
        )
        self.ProvDocument = ProvDocument()
        self.project = project
        self.project.document = self.ProvDocument
        self._dot = prov_to_dot(self.ProvDocument)
        self._entities = dict()
        self._activities = dict()
        self._agents = dict()

        # Don't add attributes if you plan on exporting to graphic format
        self.add_attributes = add_attributes

        # Default actions to create the document
        if _add_project_namespaces:
            self._add_project_namespaces()

        if _iter_envs_and_users:
            self._iter_envs_and_users()

        if _iter_samples:
            self._iter_samples()

    def __repr__(self):
        return "BioProvDocument describing Project '{}' with {} samples.".format(
            self.project.tag, len(self.project)
        )

    @property
    def dot(self):
        return prov_to_dot(self.ProvDocument)

    @dot.setter
    def dot(self, value):
        self._dot = value

    def _add_project_namespaces(self):
        """
        Runs the three _add_namespace functions.
        :return:
        """
        self._add_project_namespace()
        self._add_env_and_user_namespace()
        self._add_samples_namespace()
        self._add_activities_namespace()

    def _add_project_namespace(self):
        """
        Creates the Project Namespace and Project Entity.
        # Sets the default Namespace of the BioProvDocument as the Project.

        :return: updates self.project and self.ProvDocument.
        """
        self.project.namespace = self.ProvDocument.add_namespace(
            "project", str(self.project)
        )
        # # I may add this later
        # self.ProvDocument.set_default_namespace(self.project.namespace)

        if self.add_attributes:
            self.project.entity = self.ProvDocument.entity(
                f"project:{self.project}",
                other_attributes=build_prov_attributes(
                    {
                        k: v
                        for k, v in self.project.__dict__.items()
                        if k not in ("_samples", "files")
                    },
                    self.project.namespace,
                ),
            )
        else:
            self.project.entity = self.ProvDocument.entity(f"project:{self.project}")

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

    def _iter_envs_and_users(self):
        for _user, _env_dict in self.project.users.items():
            _user_preffix = f"users:{_user}"
            _user_bundle = self.ProvDocument.bundle(_user_preffix)
            _user_bundle.set_default_namespace(_user)
            _user_bundle.add_namespace(
                "envs", f"Environments associated with User '{_user}'"
            )
            self._agents[_user] = _user_bundle.agent(_user_preffix)
            for _env_hash, _env in _env_dict.items():
                if self.add_attributes:
                    self._entities[_env_hash] = _user_bundle.entity(
                        f"envs:{_env}",
                        other_attributes=build_prov_attributes(
                            _env.env_dict, _env.env_namespace
                        ),
                    )
                else:
                    self._entities[_env_hash] = _user_bundle.entity(f"envs:{_env}")
                _user_bundle.wasAttributedTo(
                    self._entities[_env_hash], self._agents[_user]
                )

    def _iter_samples(self):
        for _, sample in self.project.items():
            self._create_sample_bundle(sample)
            self._create_sample_file_entities(sample)
            self._create_program_entities(sample)

    def _create_sample_bundle(self, sample):
        """
        Creates a ProvBundle for the Sample and associates it to self.ProvDocument.

        :param sample: instance of bioprov.Sample
        :return: updates self.ProvDocument by creating PROV objects for the sample.
        """
        # Sample PROV attributes: bundle, namespace, entity
        sample.ProvBundle = self.ProvDocument.bundle(sample.namespace_preffix)
        sample.ProvBundle.set_default_namespace(sample.name)
        self._entities[sample.name] = sample.ProvBundle.entity(f"samples:{sample.name}")
        self.ProvDocument.wasDerivedFrom(
            self._entities[sample.name], self.project.entity
        )

    def _create_sample_file_entities(self, sample):
        """
        Creates a ProvBundle for the Sample and associates it to self.ProvDocument.

        :param sample: instance of bioprov.Sample
        :return: updates the sample.ProvBundle by creating PROV objects for the files.

        """
        sample.files_namespace_preffix = f"{sample.name}.files"
        sample.ProvBundle.add_namespace(
            sample.files_namespace_preffix,
            f"Files associated with Sample {sample.name}",
        )

        # Files PROV attributes: namespace, entities
        for key, file in sample.files.items():
            # Create Namespace
            file.namespace = sample.ProvBundle.add_namespace(file.name, str(file.path))

            # Same function call, but in the first we pass the 'other_attributes' argument
            if self.add_attributes:
                self._entities[file.name] = sample.ProvBundle.entity(
                    f"{sample.files_namespace_preffix}:{file.name}",
                    other_attributes=build_prov_attributes(
                        file.serializer(), file.namespace
                    ),
                )
            else:
                self._entities[file.name] = sample.ProvBundle.entity(
                    f"{sample.files_namespace_preffix}:{file.name}",
                )

            # Adding relationships
            sample.ProvBundle.wasDerivedFrom(
                self._entities[file.name],
                self._entities[sample.name],
            )

    def _create_program_entities(self, sample):
        # Programs PROV attributes: namespace, entities
        programs_namespace_prefix = f"{sample.name}.programs"
        programs_namespace = sample.ProvBundle.add_namespace(
            programs_namespace_prefix,
            f"Programs associated with Sample {sample.name}",
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

            self.ProvDocument.wasDerivedFrom(
                self._activities[program.name], self._entities[last_run.env]
            )

            inputs, outputs = self._get_IO_from_params(program)
            self._add_IO_relationships(sample, program, inputs, "input")
            self._add_IO_relationships(sample, program, outputs, "output")

    def _add_IO_relationships(self, sample, program, io_list, io_type):
        # To-do: replace Sample for Project when implementing Project.files and programs

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
        assert io_type in choices, Warnings()["choices"](io_type, "io_type", choices)

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
        Add activities Namespace to self
        :return:
        """

        if len(self.ProvDocument.namespaces) == 0:
            self.ProvDocument.add_namespace(
                "activities",
                f"Activities associated with bioprov Project '{self.project.tag}'",
            )
