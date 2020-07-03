"""
Contains the Sample and SampleSet classes and related functions.
"""

import pandas as pd
from bioprov.File import File
from bioprov.SequenceFile import SequenceFile
from bioprov.utils import random_string
from types import GeneratorType


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

    def add_files(self, files):
        """
        Adds file(s) to self.files. Must be a dict or an instance or iterable of bioprov.File.
        :param files: bioprov.File list, instance or dict with key, value where value is the file path.
        :return: Updates self by adding the file to self.files
        """

        # If it is a dict, we convert to File instances
        if isinstance(files, dict):
            files = {k: File(v, tag=k) for k, v in files.items()}

        # If it is an iterable of File instances, transform to a dict
        elif isinstance(files, list):
            files = {file.name: file for file in files}

        # If it is a single item, also transform to dict
        elif isinstance(files, File):
            files = {
                files.tag: files
            }  # Grabs by tag because it is File.name by default

        # Here files must be a dictionary of File instances
        for k, v in files.items():
            if k in self.files.keys():
                print(f"Updating file {k} with value {v}.")
            self.files[k] = v


class SampleSet:
    """
    Class which holds a dictionary of Sample instances, where each key is the sample name.
    """

    def __init__(self, samples=None, tag=None):
        """
        Initiates the object by creating a sample dictionary.
        :param samples: An iterator of Sample objects.
        :param tag: A tag to describe the SampleSet.
        """
        samples = self.is_iterator(
            samples
        )  # Checks if `samples` is a valid constructor.
        samples = self.build_sample_dict(samples)
        self._samples = samples
        self.tag = tag

    def __len__(self):
        return len(self._samples)

    def __getitem__(self, item):
        return self._samples[item]

    def __setitem__(self, key, value):
        self._samples[key] = value

    def keys(self):
        return self._samples.keys()

    def values(self):
        return self._samples.values()

    def items(self):
        return self._samples.items()

    def __repr__(self):
        return f"SampleSet with {len(self._samples)} samples."

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
        :param constructor: constructor object used to build a SampleSet instance.
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
            sample = SampleSet.is_sample_and_name(sample)
            samples[sample.name] = sample

        return samples

    pass


def from_df(
    df, index_col=0, file_cols=None, sequencefile_cols=None, tag=None,
):
    """
    Pandas-like function to build a SampleSet object.

    By default, assumes the sample names or ids are in the first column,
        else they should be specified by 'index_col' arg.
    '''
    samples = from_df('sample.tsv', sep="\t")

    type(samples)  # bioprov.Sample.SampleSet.
    '''
    :param df: A pandas DataFrame
    :param index_col: A column to be used as index
    :param file_cols: Columns containing Files.
    :param sequencefile_cols: Columns containing SequenceFiles.
    :param tag: A tag to describe the SampleSet.
    :return: a SampleSet instance
    """
    if index_col:
        assert (
            index_col in df.columns
        ), f"Index column '{index_col}' not present in columns!"
    else:  # Get the first column.
        index_col = df.columns[index_col]
    df.set_index(index_col, inplace=True)

    samples = dict()
    attribute_cols = [
        i for i in df.columns if i not in (file_cols, sequencefile_cols, index_col)
    ]
    for ix, row in df.iterrows():
        sample = Sample(name=ix)

        for arg, type_ in zip((file_cols, sequencefile_cols), ("file", "sequencefile")):
            if arg is not None:
                if isinstance(arg, str):  # If a string is passed,
                    arg = (arg,)  # we must make a list/tuple so we can iterate.
                for column in arg:
                    if type_ == "file":
                        sample.add_files(File(path=row[column], tag=column))
                    elif type_ == "sequencefile":
                        sample.add_files(SequenceFile(path=row[column], tag=column))
        if (
            len(attribute_cols) > 0
        ):  # Here we check by len() instead of none because it is a list.
            for attr_ in attribute_cols:
                sample.attributes[attr_] = row[attr_]
        samples[ix] = sample

    samples = SampleSet(samples, tag=tag)

    return samples

    pass


def read_csv(df, sep=",", **kwargs):
    """
    :param df: Path of dataframe.
    :param sep: Separator of dataframe.
    :param kwargs: Any kwargs to be passed to from_df()
    :return: A SampleSet instance.
    """
    df = pd.read_csv(df, sep=sep)
    ss = from_df(df, **kwargs)
    return ss
