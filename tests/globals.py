"""Global variables to be imported into test modules"""
import os

import docker


DOCKER_CLIENT = docker.from_env()
MONGODB_CONTAINER_NAME = "mongodb_test"
MONGODB_DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    "test_data",
    "mongodb_data",
)
TEST_DB_HOST = "mongodb://admin:admin@localhost:27017/?authSource=admin"
