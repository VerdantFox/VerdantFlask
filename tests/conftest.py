"""Tests global fixture file"""
import os

import pytest
from bson.objectid import ObjectId
from werkzeug.datastructures import FileStorage

from src.factory import create_app
from src.globals import PROJECT_ROOT_PATH
from src.routes.users.models import User
from tests.globals import DOCKER_CLIENT, MONGODB_CONTAINER_NAME, MONGODB_DATA_DIR
from tests.mongodb_helpers import (
    delete_all_docs,
    drop_database,
    remove_mongodb_container,
)

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------
TEST_IMAGES_PATH = os.path.join(PROJECT_ROOT_PATH, "test_data", "images")
EXAMPLE_IMAGES_DIR = os.path.join(TEST_IMAGES_PATH, "example_images")
EXAMPLE_IMAGE_PATHS = [
    os.path.join(EXAMPLE_IMAGES_DIR, image)
    for image in os.listdir(EXAMPLE_IMAGES_DIR)
    if image.split(".")[-1] in ("jpg", "jpeg", "png", "gif")
]

STANDARD_USER = {
    "id": ObjectId(),
    "username": "testuser",
    "full_name": "Test User",
    "access_level": 2,
}

ADMIN_USER = {
    "id": ObjectId(),
    "username": "adminuser",
    "full_name": "Admin User",
    "access_level": 1,
}


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


def mock_current_user(mocker, user_dict):
    """Mock a current user"""
    user = User(**user_dict)

    def fake_get_user():
        """Get a fake user"""
        return user

    mocker.patch("flask_login.utils._get_user", fake_get_user)

    return user


def get_image_path(image):
    """Get filesystem image path"""
    return os.path.join(
        PROJECT_ROOT_PATH, "test_data", "images", "example_images", image
    )


def get_and_decode(client, url, query_string=None, status_code=200, write_file=False):
    """GET a url, assert its status code and return decoded data"""
    response = client.get(url, query_string=query_string, follow_redirects=True)
    assert response.status_code == status_code
    data = response.data.decode()
    if write_file:
        with open("tmp/html.html", "w") as out_file:
            out_file.write(data)
    return data


def post_and_decode(client, url, data, status_code=200, write_file=False):
    """POST to a url, assert its status code and return decoded data"""
    response = client.post(url, data=data, follow_redirects=True)
    assert response.status_code == status_code
    data = response.data.decode()
    if write_file:
        with open("tmp/html.html", "w") as out_file:
            out_file.write(data)
    return data


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
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


@pytest.fixture(scope="module")
def delete_users_mod():
    """Delete all users in collection per module

    This is preferable to dropping the collection entirely as the indexes
    (which are slow to create) will remain intact.
    """
    delete_all_docs("users")
    yield
    delete_all_docs("users")


@pytest.fixture
def delete_users():
    """Delete all users in collection

    This is preferable to dropping the collection entirely as the indexes
    (which are slow to create) will remain intact.
    """
    delete_all_docs("users")
    yield
    delete_all_docs("users")


@pytest.fixture
def delete_budgets():
    """Delete all budgets in collection

    This is preferable to dropping the collection entirely as the indexes
    (which are slow to create) will remain intact.
    """
    delete_all_docs("budget")
    yield
    delete_all_docs("budget")


@pytest.fixture(scope="module")
def delete_blogposts_mod():
    """Delete all blog posts in collection per module

    This is preferable to dropping the collection entirely as the indexes
    (which are slow to create) will remain intact.
    """
    delete_all_docs("blog")
    yield
    delete_all_docs("blog")


@pytest.fixture
def delete_blogposts():
    """Delete all blog posts in collection

    This is preferable to dropping the collection entirely as the indexes
    (which are slow to create) will remain intact.
    """
    delete_all_docs("blog")
    yield
    delete_all_docs("blog")


@pytest.fixture
def current_user_standard(mocker):
    """Get a standard mocked current user"""
    return mock_current_user(mocker, STANDARD_USER)


@pytest.fixture
def current_user_admin(mocker):
    """Get an admin mocked current user"""
    return mock_current_user(mocker, ADMIN_USER)


@pytest.fixture(params=EXAMPLE_IMAGE_PATHS)
def example_image(request):
    """Prepare example images for testing"""
    with open(request.param, "rb") as fp:
        yield FileStorage(fp)


@pytest.fixture
def bad_image_type():
    """Yields gif filesystem image for testing"""
    with open(get_image_path("test_svg.svg"), "rb") as fp:
        yield FileStorage(fp)
