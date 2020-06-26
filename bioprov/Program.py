"""
Contains the Program class and related functions.
"""
import subprocess
from pathlib import Path


class Program:
    """
    Class for holding information about programs.
    """

    def __init__(
        self, name, params=None, tag=False, path=False, cmd=False,
    ):
        """
        :param name: Name of the program being called.
        :param params: String of parameters to add.
        :param tag: Tag to call the program if different from name. Default: self.name
        :param path: A full path to the program's binary. Default: get from self.name.
        :param cmd: A command string to call the program. Default: build from self.path and self.params.
        """
        self.name = name
        self.params = params
        self.tag = tag
        self.path = path
        self.cmd = cmd
        if not tag:
            self.tag = self.name
        if not path:
            self.path = subprocess.getoutput("which {}".format(self.name))
        if not cmd:
            self.cmd = " ".join([self.path, self.params])

    def __repr__(self):
        return self.cmd.replace(self.path, Path(self.path).stem)

    def run(self):
        pass

    pass


name, params = "prodigal", "-h"
program = Program(name, params)
