"""Tests global fixture file"""
import os

import pytest

from root.factory import create_app
from tests.globals import DOCKER_CLIENT, MONGODB_CONTAINER_NAME, MONGODB_DATA_DIR
from tests.mongodb_helpers import (
    delete_all_docs,
    drop_database,
    remove_mongodb_container,
)


@pytest.fixture(scope="session", autouse=True)
def mongodb_container(tmpdir_factory):
    """Create a fresh mongodb container and db"""

    remove_mongodb_container()
    environment = {
        "MONGO_INITDB_ROOT_USERNAME": "admin",
        "MONGO_INITDB_ROOT_PASSWORD": "admin",
    }
    volumes = {MONGODB_DATA_DIR: {"bind": "/data/db"}}
    mongodb_container = DOCKER_CLIENT.containers.run(
        image="mongo:latest",
        detach=True,
        name=MONGODB_CONTAINER_NAME,
        ports={27017: 27017},
        environment=environment,
        volumes=volumes,
    )
    drop_database()

    yield mongodb_container

    drop_database()
    remove_mongodb_container()


@pytest.fixture
def client():
    """Create a fresh flask client for a function"""
    app = start_app()

    with app.test_client() as client:
        ctx = app.app_context()
        ctx.push()
        yield client
        ctx.pop()


@pytest.fixture(scope="module")
def client_module():
    """Create a fresh, separate flask client for a module"""
    app = start_app()

    with app.test_client() as client:
        ctx = app.app_context()
        ctx.push()
        yield client
        ctx.pop()


@pytest.fixture
def drop_db():
    """Drop the flask db before and after function

    Consider dropping documents instead to preserve expensive indexes
    """
    pymongo_client = drop_database()
    yield pymongo_client
    drop_database()


@pytest.fixture
def delete_users():
    """Delete all users in collection

    This is preferable to dropping the collection entirely as the indexes
    (which are slow to create) will remain intact.
    """
    delete_all_docs("users")
    yield
    delete_all_docs("users")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def start_app():
    """start flask app"""
    os.environ["PYTEST"] = "1"
    app = create_app()

    app.config["TESTING"] = True
    app.config["BCRYPT_LOG_ROUNDS"] = 4
    app.config["WTF_CSRF_ENABLED"] = False
    return app
