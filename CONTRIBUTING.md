# Contributing

So you want to contribute to BioProv? That's great! Contributions are welcome, and every little bit helps.

There are many ways to contribute:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/vinisalazar/BioProv/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.
* The full error log! Please format it by wrapping it around "```" as it makes it more readable.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.
Post a response to the issue so we can assign it to you!

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.
Post a response to the issue so we can assign it to you!

### Write Documentation

We could always use more documentation, whether as part of the official docs, in docstrings, or even as articles and use cases.

Saw a function or class in the source code without a docstring? Write it!
Take other functions as examples of how to write docstrings.

Want to write a new tutorial for a functionality of BioProv you frequently use? Do it!
We'd prefer if you wrote the tutorial as a Jupyter Notebook (.ipynb) and added it to the docs/tutorials directory.

### Request a new feature

The best way to do so is to file an issue at https://github.com/vinisalazar/BioProv/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, so don't take it the wrong way if we take a while to respond :)
* Feeling like you could tackle writing it yourself? Go ahead!

## Get Started!

Ready to contribute? Here's how to set up BioProv for local development.

* Fork the BioProv repo on GitHub. (Top right)

* Clone your fork locally:

```bash
git clone git@github.com:your_name_here/BioProv.git
```

* Create a development environment. If you aren't yet familiar, get to know [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html), the software used to manage our environment.

```bash
conda env create --file environment.yml
```

In case you've already created the environment and changes have been made to it, run:

```bash
conda activate bioprov
conda env update --file environment.yml
```

* Assuming you've created the environment, install the package locally:

```bash
pip install -e .
```

This will make an "editable" version of the local installation.

* Update the repository to its latest version:

```bash
git pull origin master
```

* Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

Now you can make your changes locally.

* When you're done making changes, check that your changes are black-formatted and pass the tests:

```bash
black bioprov/
pytest
```

Some tests will require external tools, such as [Prodigal](https://github.com/hyattpd/Prodigal),
and if you haven't yet, you can either download them or run only a subset of tests, such as:

```bash
pytest bioprov/tests/test_bioprov_imports.py 
```

* Commit your changes and push your branch to GitHub:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

* Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, if your pull request includes code changes check that it meets these guidelines:

* If the pull request adds functionality:
    * Put your new functionality into a function or class with a docstring;
    * Make a new test for said functionality.
* Add a one-line description of the contribution to the CHANGELOG.md file under the current development version.
* Make sure your code changes were formatted with the Black styling tool.
