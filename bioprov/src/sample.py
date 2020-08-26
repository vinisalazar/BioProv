__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.0"


"""
Contains the Sample and Project classes and related functions.
"""

import json
import pandas as pd
from bioprov.src.file import File
from bioprov.src.sequencefile import SequenceFile
from bioprov.utils import random_string
from types import GeneratorType
from copy import copy
from pathlib import Path


class Sample:
    """
    Class for holding sample information and related files and programs.
    """

    def __init__(self, name=None, tag=None, files=None, attributes=None):
        """
        :param name:  Sample name or ID.
        :param tag: optional tag describing the sample.
        :param files: Dictionary of files associated with the sample.
        :param attributes: Dictionary of any other attributes associated with the sample.
        """
        if isinstance(name, str):
            name = name.replace(" ", "_")  # No space, will use it for filenames.

        self.name = name
        self.tag = tag
        if isinstance(files, dict):
            files_ = dict()
            for k, v in files.items():
                if isinstance(v, File):
                    files_[k] = v
                else:  # if not a File instance, create one.
                    files_[k] = File(path=v, tag=k)
            files = files_
        elif files is None:
            files = dict()
        self.files = files
        if attributes is not None:
            assert isinstance(attributes, dict)
        else:
            attributes = dict()
        self.attributes = attributes

    def __repr__(self):
        str_ = f"Sample {self.name} with {len(self.files)} file(s)."
        return str_

    def __getitem__(self, item):
        return self.files[item]

    def __setitem__(self, key, value):
        assert isinstance(
            value, (File, SequenceFile)
        ), f"To create file in sample, must be either a bioprov.File or bioprov.SequenceFile instance."
        self.files[key] = value

    def add_files(self, files):
        """
        Sample method to add files.
        :param files: See input to add_files function.
        :return: Adds files to Sample
        """
        add_files(self, files)

    def to_json(self, path=None, dict_only=False, _print=True):
        """
        Exports the Project as JSON. Similar to Sample.to_json()
        :param path: JSON output file path.
        :param dict_only: Whether to return the dictionary only or write the JSON.
        :param _print: Whether to print if the file was created correctly.
        :return:
        """
        if path is None:
            path = Path.joinpath(Path("./"), Path(self.name + ".json"))
            self.add_files(File(path, "json"))

        return to_json(self, path, dict_only=dict_only, _print=_print)

    def run(self, program, _print=True):
        """
        Run a Program or PresetProgram on Sample.
        :param program: An instance of bioprov.Program or PresetProgram
        :param _print: Whether to print output of Program.
        :return: Runs the program for Sample.
        """
        program.run(sample=self, _print=print)


class Project:
    """
    Class which holds a dictionary of Sample instances, where each key is the sample name.
    """

    def __init__(self, samples=None, tag=None):
        """
        Initiates the object by creating a sample dictionary.
        :param samples: An iterator of Sample objects.
        :param tag: A tag to describe the Project.
        """
        samples = self.is_iterator(
            samples
        )  # Checks if `samples` is a valid constructor.
        samples = self.build_sample_dict(samples)
        self._samples = samples
        self.files = dict()
        self.tag = tag

    def __len__(self):
        return len(self._samples)

    def __repr__(self):
        return f"Project with {len(self._samples)} samples."

    def __getitem__(self, item):
        try:
            value = self._samples[item]
            return value
        except KeyError:
            keys = self.keys()
            print(
                f"Sample {item} not in Project.\n",
                "Check the following keys:\n",
                "\n".join(keys),
            )

    def __setitem__(self, key, value):
        self._samples[key] = value

    def keys(self):
        return self._samples.keys()

    def values(self):
        return self._samples.values()

    def items(self):
        return self._samples.items()

    def add_files(self, files):
        """
        Project method to add files.
        :param files: See input to add_files function.
        :return: Adds files to Project
        """
        add_files(self, files)

    @staticmethod
    def is_sample_and_name(sample):
        """
        Checks if an object is of the Sample class.
        Name the sample if it isn't named.
        :param sample: an object of the Sample class.
        :return:
        """
        # Check class
        assert isinstance(sample, Sample), f"{sample} is not a valid Sample object!"

        # Name
        if sample.name is None:
            sample.name = random_string()

        return sample

    @staticmethod
    def is_iterator(constructor):
        """
        Checks if the constructor passed is a valid iterable, or None.
        :param constructor: constructor object used to build a Project instance.
        :return:.
        """
        assert type(constructor) in (
            list,
            dict,
            tuple,
            GeneratorType,
            type(None),
        ), f"'samples' must be an iterator of Sample instances."

        return constructor

    @staticmethod
    def build_sample_dict(constructor):
        """
        Build sample dictionary from passed constructor.
        :param constructor: Iterable or NoneType
        :return: dictionary of sample instances.
        """
        samples = dict()
        if constructor is None:
            return samples

        if isinstance(constructor, dict):
            constructor = list(constructor.values())

        for sample in constructor:
            sample = Project.is_sample_and_name(sample)
            samples[sample.name] = sample

        return samples

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, value):
        self._samples = self.build_sample_dict(value)

    def to_json(self, path=None, dict_only=False, _print=True):
        """
        Exports the Project as JSON. Similar to Sample.to_json()
        :param path: JSON output file path.
        :param dict_only: Whether to return the dictionary only or write the JSON.
        :param _print: Whether to print if the file was created correctly.
        :return:
        """
        if path is None:
            if self.tag is not None:
                path = f"./{self.tag}.json"
            else:
                pass
        return to_json(self, path, dict_only=dict_only, _print=_print)


def add_files(object_, files):
    """
        Adds file(s) to object. Must be a dict or an instance or iterable of bioprov.File.
        :param object_: A Sample or Project instance.
        :param files: bioprov.File list, instance or dict with key, value where value is the file path.
        :return: Updates self by adding the file to object.
        """

    # Assert it is adding to correct object
    assert isinstance(
        object_, (Sample, Project)
    ), "Can't add file to type '{}'. Can only add file to Sample or Project object.".format(
        type(object_)
    )

    # If it is a dict, we convert to File instances
    if isinstance(files, dict):
        files = {k: File(v, tag=k) for k, v in files.items()}

    # If it is an iterable of File instances, transform to a dict
    elif isinstance(files, list):
        files = {file.name: file for file in files}

    # If it is a single item, also transform to dict
    elif isinstance(files, File):
        files = {files.tag: files}  # Grabs by tag because it is File.name by default

    # Here files must be a dictionary of File instances
    for k, v in files.items():
        if k in object_.files.keys():
            print(f"Updating file {k} with value {v}.")
        object_.files[k] = v


def to_json(samplelike, path=None, dict_only=False, _print=True):
    """
    Exports the Sample or Project as JSON.
    :param samplelike: Sample or Project instance.
    :param path: Path to JSON file. Default is current directory.
    :param dict_only: Whether to return a dictionary only or write the JSON.
    :param _print: Whether to print if the file was created correctly.
    :return:
    """
    json_out = dict()

    assert isinstance(
        samplelike, (Project, Sample)
    ), f"{samplelike} must be a Sample or Project object!"

    # Build Project JSON dict
    if isinstance(samplelike, Project):
        project = samplelike
        if path is None:
            path = f"./Project_{random_string()}.json"
        for name, sample in project.items():
            json_out[name] = sample.to_json(dict_only=True, _print=False)

    # Build Sample JSON dict
    elif isinstance(samplelike, Sample):
        sample = samplelike
        if path is None:
            path = Path.joinpath(Path("./"), Path(sample.name + ".json"))
            sample.add_files(File(path, "json"))

        for key, value in sample.__dict__.items():
            key_, value_ = copy(key), copy(value)  # Create copies, not reference
            if isinstance(value, dict):  # Or we will lose our original values.
                for k, v in value_.items():
                    value_[k] = str(v)
            json_out[key] = value_

    if dict_only:
        return json_out

    write_json(json_out, path)

    return


def from_json(json_file, kind="Sample"):
    """
    Imports Sample or Project from JSON file.
    :param json_file: A JSON file created by Sample.to_json()
    :param kind: Whether to create a Sample or Project instance.
    :return: a Sample or Project instance.
    """
    assert kind in ("Sample", "Project"), "Must specify 'Sample' or 'Project'."
    d = json_to_dict(json_file)
    if "name" in d.keys():  # This checks whether the file is a Sample or Project
        kind = "Sample"  # To-do: must be improved.
    else:
        kind = "Project"
    if kind == "Sample":
        sample_ = dict_to_sample(d)
        return sample_
    elif kind == "Project":
        samples = dict()
        for k, v in d.items():
            samples[k] = dict_to_sample(v)
        sampleset = Project(samples=samples)
        return sampleset


def from_df(
    df,
    index_col=0,
    file_cols=None,
    sequencefile_cols=None,
    tag=None,
    source_file=None,
    import_data=False,
):
    """
    Pandas-like function to build a Project object.

    By default, assumes the sample names or ids are in the first column,
        else they should be specified by 'index_col' arg.
    '''
    samples = from_df(df_path, sep="\t")

    type(samples)  # bioprov.Sample.Project.

    You can select columns to be added as Files or SequenceFile instances.
    '''
    :param df: A pandas DataFrame
    :param index_col: A column to be used as index. Must be in df_path.columns.
                        If int is passed, will get it from columns.
    :param file_cols: Columns containing Files.
    :param sequencefile_cols: Columns containing SequenceFiles.
    :param tag: A tag to describe the Project.
    :param source_file: The source file used to read the dataframe.
    :param import_data: Whether to import data when importing SequenceFiles
    :return: a Project instance
    """
    df_ = df.copy()
    if isinstance(index_col, int):
        index_col = df_.columns[index_col]
    assert (
        index_col in df_.columns
    ), f"Index column '{index_col}' not present in columns!"
    df_.set_index(index_col, inplace=True)

    samples = dict()
    attribute_cols = [
        i for i in df_.columns if i not in (file_cols, sequencefile_cols, index_col)
    ]
    for ix, row in df_.iterrows():
        sample = Sample(name=ix)

        for arg, type_ in zip((file_cols, sequencefile_cols), ("file", "sequencefile")):
            if arg is not None:
                if isinstance(arg, str):  # If a string is passed,
                    arg = (arg,)  # we must make a list/tuple so we can iterate.
                for column in arg:
                    if type_ == "file":
                        sample.add_files(File(path=row[column], tag=column))
                    elif type_ == "sequencefile":
                        sample.add_files(
                            SequenceFile(
                                path=row[column], tag=column, import_data=import_data
                            )
                        )
        if (
            len(attribute_cols) > 0
        ):  # Here we check by len() instead of none because it is a list.
            for attr_ in attribute_cols:
                sample.attributes[attr_] = row[attr_]
        samples[ix] = sample

    samples = Project(samples, tag=tag)
    if source_file:
        samples.add_files({"project_csv": source_file})

    return samples

    pass


def read_csv(df_path, sep=",", **kwargs):
    """
    :param df_path: Path of dataframe.
    :param sep: Separator of dataframe.
    :param kwargs: Any kwargs to be passed to from_df()
    :return: A Project instance.
    """
    df = pd.read_csv(df_path, sep=sep)
    sampleset = from_df(df, source_file=df_path, **kwargs)
    return sampleset


def json_to_dict(json_file):
    """
    Reads dict from a JSON file.
    :param json_file: A JSON file created by Sample.to_json()
    :return: a dictionary (input to dict_to_sample())
    """
    with open(json_file) as f:
        dict_ = json.load(f)
    return dict_


def dict_to_sample(json_dict):
    """
    Converts a JSON dictionary to a sample instance.
    :param json_dict: output of sample_from_json.
    :return: a Sample instance.
    """
    sample_ = Sample()
    for attr, value in json_dict.items():
        # Create File instances
        if attr == "files":
            for tag, path in value.items():
                value[tag] = File(path, tag)

        setattr(sample_, attr, value)
    return sample_


def write_json(dict_, path, _print=True):
    """
    Writes dictionary to JSON file.
    :param dict_: JSON dictionary.
    :param path: String with path to JSON file.
    :param _print: Whether to print if the file was successfully created.
    :return: Writes JSON file
    """
    with open(path, "w") as f:
        json.dump(dict_, f, indent=3)

    if _print:
        if Path(path).exists():
            print(f"Created JSON file at {path}.")
        else:
            print(f"Could not create JSON file for {path}.")
