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
def user1_mod(client_module):
    """Create a fresh user for testing"""
    new_user = setup_create_user(USER1)
    yield new_user
    new_user.delete()


@pytest.fixture(scope="module")
def user2_mod(client_module):
    """Create a fresh user for testing with sharing == False"""
    new_user = setup_create_user(USER2)
    yield new_user
    new_user.delete()


@pytest.fixture()
def logged_in_user1_mod(client, user1_mod):
    """Log in the created user"""
    yield login_user(client, user1_mod)


@pytest.fixture()
def logged_in_user2_mod(client, user2_mod):
    """Log in the created user"""
    yield login_user(client, user2_mod)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def setup_create_user(user_dict):
    """Common setup for create user"""
    new_user = User(**user_dict)
    new_user.save()
    for key, val in user_dict.items():
        assert new_user[key] == val
    return new_user


def login_user(cl, usr):
    """Common setup for loggin in user"""
    form_data = {"username_or_email": usr.username, "password": PASSWORD}
    response = cl.post("/users/login", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert f"Welcome {usr.username}!" in response.data.decode()
    return usr
