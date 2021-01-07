#!/usr/env/bin python


import argparse
import bioprov as bp
from os import path


def _load_project(tag):
    _proj = bp.load_project(tag)
    _proj.auto_update = True
    return _proj


def _run_programs(_proj):
    for k, sample in _proj.items():
        sample.run_programs()
    for k, program in _proj.programs.items():
        if program.name not in ("ncbi-genome-download", "sort", "gunzip", "sed"):
            program.run()


def _write_programs(_proj):
    output = f"{_proj.tag}_cmd.sh"
    with open(output, "w") as f:
        f.write("#!/usr/bin/bash\n\n")
        for k, sample in _proj.items():
            for k_, program in sample.programs.items():
                f.write(f"# {program.name} for Sample '{sample.name}'\n")
                f.write(program.cmd + "\n\n")
        for k, program in _proj.programs.items():
            if k not in (
                "ncbi-genome-download",
                "sort",
                "gunzip",
                "sed",
                "sed_gz",
                "sed_column",
            ):
                f.write(f"# {program.name}\n")
                f.write(program.cmd + "\n\n")

    if path.isfile(output):
        print(f"Wrote programs for project '{_proj.tag}' to {output}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load and run programs with BioProv.")
    parser.add_argument("-t", "--tag", help="Project tag to load.", required=True)
    parser.add_argument(
        "-w", "--write", help="Write programs to file.", action="store_true"
    )
    args = parser.parse_args()

    proj = _load_project(args.tag)

    if args.write:
        _write_programs(proj)
    else:
        _run_programs(proj)
