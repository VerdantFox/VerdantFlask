"""Users functional tests fixture file"""
from datetime import datetime

import pytest
from werkzeug.security import generate_password_hash

from src.routes.users.models import User

USERNAME = "testuser"
FULL_NAME = "Test User"
EMAIL = "testuser@email.com"
PASSWORD = "testuserpass1"
PASSWORD_HASH = generate_password_hash(PASSWORD)
USER1 = {
    "username": USERNAME,
    "email": EMAIL,
    "share_email": True,
    "password_hash": PASSWORD_HASH,
    "full_name": FULL_NAME,
    "share_name": True,
    "avatar_location": "/some/av/location.png",
    "bio": "Some fake bio.",
    "birth_date": datetime(1980, 4, 23),
    "share_birth_date": True,
    "timezone": "US/Pacific",
    "share_timezone": True,
}
USER2 = {
    "username": "usernametwo",
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
    "facebook_id": "somefakefacebookid",
    "google_id": "somefakegoogleid",
    "github_id": 123456789,
}

USER3 = {
    "username": USERNAME + "1",
    "full_name": FULL_NAME + "ophegus",
}


@pytest.fixture()
def user1(client):
    """Create a fresh user for testing individual function"""
    new_user = setup_create_user(USER1)
    yield new_user
    new_user.delete()


@pytest.fixture()
def user2(client):
    """Create a fresh user for testing individual function"""
    new_user = setup_create_user(USER2)
    yield new_user
    new_user.delete()


@pytest.fixture()
def user3(client):
    """Create a fresh user for testing individual function"""
    new_user = setup_create_user(USER3)
    yield new_user
    new_user.delete()


@pytest.fixture
def logged_in_user1(client, user1):
    """Log in the created user"""
    yield login_user(client, user1)


@pytest.fixture
def logged_in_user2(client, user2):
    """Log in the created user"""
    yield login_user(client, user2)


@pytest.fixture(scope="module")
def user1_mod(client_module):
    """Create a fresh user for testing whole module"""
    new_user = setup_create_user(USER1)
    yield new_user
    new_user.delete()


@pytest.fixture(scope="module")
def user2_mod(client_module):
    """Create a fresh user for testing with sharing == False"""
    new_user = setup_create_user(USER2)
    yield new_user
    new_user.delete()


@pytest.fixture
def revert_user1(user1_mod):
    """Revert the state of user1 before and after function

    Have to GET user from database before save every time or stale user
    won't save properly.
    """
    user = User.objects(id=user1_mod.id).first()
    save_user_fields(user, USER1)
    yield user
    user = User.objects(id=user1_mod.id).first()
    save_user_fields(user, USER1)


@pytest.fixture
def logged_in_user1_mod(client, revert_user1):
    """Log in the created user (in reverted state)"""
    yield login_user(client, revert_user1)


@pytest.fixture
def logged_in_user2_mod(client, user2_mod):
    """Log in the created user"""
    yield login_user(client, user2_mod)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def save_user_fields(user, user_dict):
    """Save a user's fields to fields defined by dictionary"""
    for key, val in user_dict.items():
        user[key] = val
    user.save()
    user_check = User.objects(id=user.id).first()
    for key, val in user_dict.items():
        assert user_check[key] == val
    return user_check


def setup_create_user(user_dict):
    """Common setup for create user"""
    return save_user_fields(User(), user_dict)


def login_user(cl, usr):
    """Common setup for loggin in user"""
    form_data = {"username_or_email": usr.username, "password": PASSWORD}
    response = cl.post("/users/login", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert f"Welcome {usr.username}!" in response.data.decode()
    return usr


def date_str_fmt(datetime_obj):
    """Conver datetime to a string object in the format displayed on pages"""
    return datetime_obj.strftime("%B %d, %Y")


def date_str_fmt_forms(datetime_obj):
    """Conver datetime to a string object in the format used in forms"""
    return datetime_obj.strftime("%Y-%m-%d")


def no_whitespace(string):
    """Remove whitespace from string"""
    return "".join(string.split())
