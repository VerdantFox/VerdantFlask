"""Users functional tests fixture file"""
import pytest
from werkzeug.security import generate_password_hash

from root.routes.users.models import User

USERNAME = "testuser"
EMAIL = "testuser@email.com"
PASSWORD = "testuserpass1"
PASSWORD_HASH = generate_password_hash(PASSWORD)


@pytest.fixture(scope="module")
def user(client):
    """Create a fresh user testing"""
    new_user = User(username=USERNAME, email=EMAIL, password_hash=PASSWORD_HASH,)
    new_user.save()
    assert new_user.username == USERNAME
    assert new_user.email == EMAIL
    assert new_user.password_hash == PASSWORD_HASH
    yield new_user
    new_user.delete()
