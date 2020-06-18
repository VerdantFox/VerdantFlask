"""Users functional tests fixture file"""
from datetime import datetime

import pytest
from werkzeug.security import generate_password_hash

from root.routes.users.models import User

USERNAME = "testuser"
EMAIL = "testuser@email.com"
PASSWORD = "testuserpass1"
PASSWORD_HASH = generate_password_hash(PASSWORD)
USER1 = {
    "username": USERNAME,
    "email": EMAIL,
    "share_email": True,
    "password_hash": PASSWORD_HASH,
    "full_name": "Test User",
    "share_name": True,
    "avatar_location": "/some/av/location.png",
    "bio": "Some fake bio.",
    "birth_date": datetime(1980, 4, 23),
    "share_birth_date": True,
    "timezone": "US/Pacific",
    "share_timezone": True,
}
USER2 = {
    "username": "user2",
    "email": "user2@gmail.com",
    "share_email": False,
    "password_hash": PASSWORD_HASH,
    "full_name": "Hidden User",
    "share_name": False,
    "avatar_location": "/some/av/location.png",
    "bio": "Some fake bio.",
    "birth_date": datetime(1980, 4, 23),
    "share_birth_date": False,
    "timezone": "US/Pacific",
    "share_timezone": False,
}


@pytest.fixture(scope="module")
def user(client_module):
    """Create a fresh user for testing"""
    new_user = User(**USER1)
    new_user.save()
    for key, val in USER1.items():
        assert new_user[key] == val
    yield new_user
    new_user.delete()


@pytest.fixture(scope="module")
def user2(client_module):
    """Create a fresh user for testing with sharing == False"""
    new_user = User(**USER2)
    new_user.save()
    for key, val in USER2.items():
        assert new_user[key] == val
    yield new_user
    new_user.delete()


@pytest.fixture()
def logged_in_user(client, user):
    """Log in the created user"""
    form_data = {"username_or_email": user.username, "password": PASSWORD}
    response = client.post("/users/login", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert f"Welcome {user.username}!" in response.data.decode()
    yield user


@pytest.fixture()
def logged_in_user2(client, user2):
    """Log in the created user"""
    form_data = {"username_or_email": user2.username, "password": PASSWORD}
    response = client.post("/users/login", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert f"Welcome {user2.username}!" in response.data.decode()
    yield user2
