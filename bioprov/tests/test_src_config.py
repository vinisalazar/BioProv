__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.20"


"""
Testing for the Config module.
"""

from os import environ, remove
from pathlib import Path
from tempfile import NamedTemporaryFile

from coolname import generate_slug
from tinydb import TinyDB, Query

import bioprov as bp
from bioprov.src.config import Config, BioProvDB


def test_Config():
    """
    Testing for the Config class
    :return:
    """
    config = Config()
    assert config.env.env_dict == dict(environ.items())
    assert config.user == config.env.user
    assert config.genomes.exists()
    assert config.data.exists()
    assert str(config) == f"BioProv Config class set in {bp.src.config.__file__}"
    assert type(len(config.db_all())) == int

    # ProvStore properties
    # getters
    if Path(config.provstore_file).is_file():
        # no cover because default is the file not existing
        assert config.provstore_user is not None  # no cover
        assert config.provstore_token is not None  # no cover
    else:
        assert config._provstore_user is None
        assert config._provstore_token is None

    # setters
    config.provstore_user = None
    config.provstore_token = None

    with NamedTemporaryFile() as f:
        config.provstore_file = f.name
        config.create_provstore_file(user=generate_slug(2), token=generate_slug(4))
        config.read_provstore_file()


def test_BioProvDB():

    # Compare to TinyDB
    db_path = Path(bp.__file__).parent.joinpath("db.json")
    bp_db = BioProvDB(db_path)
    tinydb_ = TinyDB(db_path)
    assert len(bp_db) == len(tinydb_), "BioProvDB and TinyDB behaviour differs!"
    assert isinstance(
        bp_db, type(tinydb_)
    ), f"Type {type(bp_db)} should inherit or be an instance of {type(tinydb_)}"

    # Try a Query
    q = Query()
    slug, slug_ = generate_slug(2), generate_slug(4)
    results = bp_db.search(q[slug] == slug_)
    assert results == [], f"Query result should be an empty list! Results: {results}"

    # Create and erase database
    non_db_path = "./." + generate_slug(4) + ".json"
    non_db = BioProvDB(non_db_path)
    non_db.clear_db(confirm=True)
    assert len(non_db) == 0, f"Did not correctly erase the database at {non_db_path}"
    remove(non_db_path)
