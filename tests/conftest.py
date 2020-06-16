"""Tests global fixture file"""
import os

import pytest

from root.factory import create_app
from tests.globals import (
    DOCKER_CLIENT,
    MONGODB_CONTAINER_NAME,
    MONGODB_DATA_DIR,
)
from tests.mongodb_helpers import remove_mongodb_container, drop_database


@pytest.fixture(scope="session", autouse=True)
def mongodb_container(tmpdir_factory):
    """Create a fresh, temporary database from docker and set it up"""

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


@pytest.fixture(scope="session")
def client():
    """Create a flask client"""
    os.environ["PYTEST"] = "1"
    app = create_app()

    app.config["TESTING"] = True
    app.config["BCRYPT_LOG_ROUNDS"] = 4
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        ctx = app.app_context()
        ctx.push()
        yield client
        ctx.pop()


@pytest.fixture()
def drop_db():
    """Drop the flask db before and after function"""
    pymongo_client = drop_database()
    yield pymongo_client
    drop_database()
