"""Global test variables that might need to be imported"""
import os

import docker

DOCKER_CLIENT = docker.from_env()
MONGODB_CONTAINER_NAME = "mongodb_test"
MONGODB_DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    "test_data",
    "mongodb_data",
)
MONGODB_USERNAME = "admin"
MONGODB_PASSWORD = "admin"
DB_NAME = "flask"
TEST_DB_HOST = (
    f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}"
    f"@localhost:27017/{DB_NAME}?authSource=admin"
)
