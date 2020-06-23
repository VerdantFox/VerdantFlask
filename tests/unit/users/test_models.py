"""Most basic pytest"""
from datetime import datetime

import mongoengine
import pytest
from werkzeug.security import generate_password_hash

from root.routes.users.models import User
from tests.mongodb_helpers import list_indexes

USERS_COLLECTION = "users"
USER_MODEL_DEFAULTS = {
    # field: [default, indexed]
    "username": [None, True],
    "email": [None, True],
    "share_email": [False, True],
    "password_hash": [None, True],
    "full_name": [None, True],
    "share_name": [False, True],
    "avatar_location": [None, True],
    "bio": [None, True],
    "birth_date": [None, True],
    "share_birth_date": [False, True],
    "timezone": [None, True],
    "share_timezone": [False, True],
    "access_level": [2, True],
    "facebook_id": [None, True],
    "google_id": [None, True],
    "github_id": [None, True],
}
GOOD_USERS = [
    pytest.param(
        {
            "username": "testuser1",
            "email": "testuser@gmail.com",
            "share_email": True,
            "password": "testpass",
            "full_name": "Test User",
            "share_name": True,
            "avatar_location": "/path/to/avatar.png",
            "bio": "Some cool bio.\nJust super.",
            "birth_date": datetime(1949, 10, 25),
            "share_birth_date": True,
            "timezone": "US/pacific",
            "share_timezone": True,
            "access_level": 2,
            "facebook_id": "1234556asdfasd324a",
            "google_id": "asdfasdf49879sa.asdf@asdf.com",
            "github_id": 890127340910981273,
        },
        id="everything",
    ),
    pytest.param(
        {
            "username": "testuser2",
            "email": "testuser@gmail.com",
            "password": "testpass2",
            "full_name": "abraham lincoln",
        },
        id="standard",
    ),
    pytest.param({"username": "testuser2"}, id="minimum",),
]


@pytest.mark.parametrize("user_dict", GOOD_USERS)
def test_new_user_good_succeeds(client, delete_users, user_dict):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, share_email, passwordhash, full_name,
         share_name, avatar_location, bio, birthdate, share_birth_date,
         timezone, share_timezone, access_level, github_id, facebook_id,
         google_id, is_authenticated
         fields are created correctly
    """
    hash_user_pw(user_dict)
    new_user = User(**user_dict)
    new_user.save()
    assert str(new_user) == f"User(username: {new_user.username}, id: {new_user.id})"
    for key in user_dict:
        assert new_user[key] == user_dict[key]
    for key in USER_MODEL_DEFAULTS:
        if not user_dict.get(key):
            assert new_user[key] == USER_MODEL_DEFAULTS[key][0]
    indexed_fields = {
        key
        for key, value in USER_MODEL_DEFAULTS.items()
        if value[1] is True and user_dict.get(key)
    }
    indexs_found = set(list_indexes(USERS_COLLECTION))
    assert indexed_fields.issubset(indexs_found)


BAD_USERS = [
    pytest.param({"email": "bob"}, id="no_username",),
    pytest.param({"username": "testuser", "email": "not_an_email"}, id="not_an_email",),
    pytest.param({"username": "testuser", "full_name": "a" * 81}, id="name_too_long",),
    pytest.param(
        {"username": "testuser", "avatar_location": "a" * 401}, id="name_too_long",
    ),
    pytest.param({"username": "testuser", "bio": "a" * 1001}, id="bio_too_long",),
    pytest.param(
        {"username": "testuser", "birth_date": "abc123"},
        id="birth_date_not_datetime_object",
    ),
    pytest.param(
        {"username": "testuser", "timezone": datetime(1955, 5, 5)},
        id="timezone_not_string",
    ),
    pytest.param(
        {"username": "testuser", "access_level": "one"}, id="access_level_not_int",
    ),
    pytest.param(
        {"username": "testuser", "access_level": 3}, id="access_level_outside_range",
    ),
    pytest.param(
        {"username": "testuser", "access_level": 3}, id="access_level_outside_range",
    ),
    pytest.param({"username": "testuser", "facebook_id": 3}, id="fb_id_not_string",),
    pytest.param({"username": "testuser", "google_id": 3}, id="google_id_not_string",),
    pytest.param(
        {"username": "testuser", "github_id": "asdf"}, id="github_id_not_int",
    ),
]


@pytest.mark.parametrize("user_dict", BAD_USERS)
def test_new_user_bad_fails(client, delete_users, user_dict):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check user fails when fields don't match model rules
    """
    hash_user_pw(user_dict)
    new_user = User(**user_dict)
    with pytest.raises(mongoengine.errors.ValidationError):
        new_user.save()


def test_user_check_password(client, delete_users):
    """Check the user model check_password method"""
    password = "somepassword"
    password_hash = generate_password_hash(password)
    user = User(username="testuser", password_hash=password_hash)
    user.save()
    assert user.check_password(password)


def hash_user_pw(user_dict):
    """Hashes a user password and replaces password with hashed_password"""
    password = user_dict.pop("password", None)
    if password:
        user_dict["password_hash"] = generate_password_hash(password)
        # asserts new_user.password_hash != password transitively
        assert password != user_dict["password_hash"]
    return password
