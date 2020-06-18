"""Helper functions for working with mongodb for tests"""
import docker
from pymongo import MongoClient

from tests.globals import DB_NAME, DOCKER_CLIENT, MONGODB_CONTAINER_NAME, TEST_DB_HOST


def remove_mongodb_container():
    """Remove the mongodb container"""
    try:
        container = DOCKER_CLIENT.containers.get(MONGODB_CONTAINER_NAME)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass  # Do nothing if container not found


def drop_database():
    """Drop the flask database"""
    pymongo_client = MongoClient(TEST_DB_HOST)
    pymongo_client.drop_database("flask")
    return pymongo_client


def delete_all_docs(collection_name):
    """Delete all documents in a database"""
    pymongo_client = MongoClient(TEST_DB_HOST)
    db = pymongo_client["flask"]
    db[collection_name].remove({})


def list_indexes(collection):
    """List fields indexed in the flask database"""
    pymongo_client = MongoClient(TEST_DB_HOST)
    db = pymongo_client[DB_NAME]
    collections = db.list_collection_names()
    if collection not in collections:
        raise EnvironmentError(f"{collection} not found in collections: {collections}")
    col = db[collection]
    indexes_full = col.index_information()
    # List of index names
    return [index["key"][0][0] for index in indexes_full.values()]
