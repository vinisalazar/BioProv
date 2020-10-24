__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.13"


import setuptools

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="bioprov",
    version="0.1.13",
    author="Vini Salazar",
    author_email="viniws@gmail.com",
    description="BioProv - Provenance capture for bioinformatics workflows",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/vinisalazar/BioProv",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    packages=setuptools.find_packages(),
    scripts=["bioprov/bioprov"],
    include_package_data=True,
    keywords="w3c-prov biopython biological-data provenance",
    python_requires=">=3.6",
    install_requires=[
        "biopython",
        "coolname",
        "coveralls",
        "dataclasses",
        "pandas",
        "prov",
        "pydot",
        "pytest",
        "pytest-cov",
        "tqdm",
        "tinydb",
    ],
)
