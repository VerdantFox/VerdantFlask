"""Most basic pytest"""
from root.routes.users.models import User
from werkzeug.security import generate_password_hash


def test_new_user_standard():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, share_email, passwordhash, full_name,
         share_name, avatar_location, bio, birthdate, share_birth_date,
         timezone, share_timezone, access_level, github_id, facebook_id,
         google_id, is_authenticated
         fields are created correctly
    """
    newuserhash = generate_password_hash("testhashedpass")
    new_user = User(
        username="testuser1",
        email="testuser@gmail.com",
        password_hash=newuserhash,
        full_name="Test User",
    )
    new_user.save()
    assert new_user.username == "testuser1"
    assert new_user.email == "testuser@gmail.com"
    assert new_user.share_email is False
    assert new_user.password_hash != "testhashedpass"
    assert new_user.check_password("testhashedpass") is True
    assert new_user.full_name == "Test User"
    assert new_user.share_name is False
    assert new_user.avatar_location is None
    assert new_user.bio is None
    assert new_user.share_birth_date is False
    assert new_user.timezone is None
    assert new_user.share_timezone is False
    assert new_user.access_level == 2
    assert new_user.facebook_id is None
    assert new_user.google_id is None
    assert new_user.github_id is None
    assert new_user.is_authenticated is True
    new_user.delete()
