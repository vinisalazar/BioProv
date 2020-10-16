__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.7"

"""
Module containing base provenance attributes.

This module extracts system-level information, such as user and environment
settings, and stores them. It is invoked to export provenance objects. 
"""
from bioprov import Project
from bioprov.utils import Warnings, build_prov_attributes
from prov.model import ProvDocument


class BioProvDocument:
    """
    Class containing base provenance information for a Project.
    """

    def __init__(
        self, project, _add_project_namespaces=True, add_attributes=False,
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
        self._entities = dict()
        self._activities = dict()
        self._agents = dict()
        self.add_attributes = add_attributes

        # Add default namespaces
        if _add_project_namespaces:
            self._add_project_namespaces()

        # Update relationships
        self._add_relationships()

    # def __repr__(self):
    #     return "BioProvDocument describing Project '{}' with {} samples.".format(
    #         self.project.tag, len(self.project)
    #     )

    def _add_project_namespaces(self):
        """
        Runs the three _add_namespace functions.
        :return:
        """
        self._add_project_namespace()
        self._add_samples_namespace()
        self._add_activities_namespace()
        self._add_env_and_user_namespace()
        self._iter_envs_and_users()
        self._iter_samples()

    def _add_env_and_user_namespace(self):
        self.ProvDocument.add_namespace(
            "users", f"Users associated with BioProv Project '{self.project.tag}'"
        )

    def _add_project_namespace(self):
        self.project.namespace = self.ProvDocument.add_namespace(
            "project", str(self.project)
        )
        if self.add_attributes:
            # self._entities[self.project.tag]
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
        # # Check if project_csv exists
        # if "project_csv" in self.project.files.keys():
        #     self.project_file_entity = self.ProvDocument.entity(
        #         "project:{}".format(self.project.files["project_csv"])
        #     )
        # else:
        #     pass

    def _add_samples_namespace(self):

        self.ProvDocument.add_namespace(
            "samples", f"Samples associated with bioprov Project '{self.project.tag}'",
        )

    def _iter_envs_and_users(self):

        for _user, _env in self.project.envs.items():
            _user_bundle = self.ProvDocument.bundle(f"users:{_user}")
            _user_bundle.add_namespace("envs", f"Envs associated with user '{_user}'")

            if self.add_attributes:
                self._entities[_env] = _user_bundle.entity(
                    f"envs:{_env}",
                    other_attributes=build_prov_attributes(
                        _env.env_dict, _env.env_namespace
                    ),
                )
            else:
                self._entities[_env] = _user_bundle.entity(f"envs:{_env}")

            self._agents[_user] = _user_bundle.agent(f"users:{_user}")
            self.ProvDocument.wasAttributedTo(self._entities[_env], self._agents[_user])

    def _iter_samples(self):
        for _, sample in self.project.items():

            # Sample PROV attributes: bundle, namespace, entity
            sample.ProvBundle = self.ProvDocument.bundle(f"samples:{sample.name}")
            sample.ProvBundle.set_default_namespace(sample.name)
            self._entities[sample.name] = sample.ProvBundle.entity(
                f"samples:{sample.name}"
            )
            self.ProvDocument.wasDerivedFrom(
                self._entities[sample.name], self.project.entity
            )

            # Files PROV attributes: namespace, entities
            files_namespace_prefix = f"{sample.name}.files"
            sample.ProvBundle.add_namespace(
                files_namespace_prefix, f"Files associated with Sample {sample.name}",
            )
            for key, file in sample.files.items():

                # Create Namespace
                file.namespace = sample.ProvBundle.add_namespace(
                    file.name, str(file.path)
                )

                # Add atributes or not
                if self.add_attributes:
                    self._entities[file.name] = sample.ProvBundle.entity(
                        f"{files_namespace_prefix}:{file.name}",
                        other_attributes=build_prov_attributes(
                            file.__dict__, file.namespace
                        ),
                    )
                else:
                    self._entities[file.name] = sample.ProvBundle.entity(
                        f"{files_namespace_prefix}:{file.name}",
                    )

                # Adding relationships
                sample.ProvBundle.wasDerivedFrom(
                    self._entities[file.name], self._entities[sample.name],
                )

            # Programs PROV attributes: namespace, entities
            programs_namespace_prefix = f"{sample.name}.programs"
            sample.ProvBundle.add_namespace(
                programs_namespace_prefix,
                f"Programs associated with Sample {sample.name}",
            )
            for key, program in sample.programs.items():
                last_run = program.runs[str(len(program.runs))]
                self._activities[program.name] = sample.ProvBundle.activity(
                    f"{programs_namespace_prefix}:{program.name}",
                    startTime=last_run.start_time,
                    endTime=last_run.end_time,
                )
                self.ProvDocument.wasAssociatedWith(
                    self._activities[program.name], f"users:{last_run.user}"
                )

                # Relationships based on Parameters
                sample_files = [str(file) for _, file in sample.files.items()]
                inputs = [
                    parameter["value"]
                    for _, parameter in program.params.items()
                    if parameter["kind"] == "input"
                ]
                outputs = [
                    parameter["value"]
                    for _, parameter in program.params.items()
                    if parameter["kind"] == "output"
                ]

                # These two for loops are nearly duplicated.
                # It can be improved.
                for value in inputs:
                    if value in sample_files:
                        file_obj = [
                            file_
                            for _, file_ in sample.files.items()
                            if str(file_) == value
                        ]
                        if file_obj:
                            file_obj = file_obj[0]
                            sample.ProvBundle.used(
                                self._entities[file_obj.name],
                                self._activities[program.name],
                            )

                for value in outputs:
                    if value in sample_files:
                        file_obj = [
                            file_
                            for _, file_ in sample.files.items()
                            if str(file_) == value
                        ]
                        if file_obj:
                            file_obj = file_obj[0]
                            sample.ProvBundle.wasGeneratedBy(
                                self._entities[file_obj.name],
                                self._activities[program.name],
                            )

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

        # # Activities
        # self.activities = {
        #     "import_Project": self.ProvDocument.activity(
        #         "activities:{}".format("bioprov.Project")
        #     ),
        #     "import_Sample": self.ProvDocument.activity(
        #         "activities:{}".format("bioprov.Sample")
        #     ),
        # }

    def _add_relationships(self):
        pass
        # Relating project with user, project file, and sample
        # self.ProvDocument.wasAttributedTo(
        #     self.project.ProvEntity, "user:{}".format(self.user)
        # )
        # # Add activities
        # for key, activity in self.activities.items():
        #     self.ProvDocument.wasAssociatedWith(activity, "user:{}".format(self.user))
        # self.ProvDocument.wasGeneratedBy(
        #     self.project.ProvEntity, self.activities["import_Project"]
        # )
        # if self.project_file_entity is not None:
        #     self.ProvDocument.used(
        #         self.activities["import_Project"], self.project_file_entity
        #     )
        # self.ProvDocument.used(self.activities["import_Sample"], self.project.ProvEntity)
        # self.ProvDocument.wasGeneratedBy(
        #     self.samples_entity, self.activities["import_Sample"]
        # )
        # self.ProvDocument.wasAttributedTo(self.env_entity, self.user_agent)
