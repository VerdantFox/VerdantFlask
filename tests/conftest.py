import os

import docker
import pytest
from pymongo import MongoClient

from root.factory import create_app

DOCKER_CLIENT = docker.from_env()
MONGODB_CONTAINER_NAME = "mongodb_test"
MONGODB_DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    "test_data",
    "mongodb_data",
)
TEST_DB_HOST = "mongodb://admin:admin@localhost:27017/?authSource=admin"


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


@pytest.fixture()
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


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def remove_mongodb_container():
    """Remove the mongodb container"""
    try:
        container = DOCKER_CLIENT.containers.get(MONGODB_CONTAINER_NAME)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass  # Do nothing if container not found


def drop_database():
    """Drop the test database"""
    pymongo_client = MongoClient(TEST_DB_HOST)
    pymongo_client.drop_database("flask")
