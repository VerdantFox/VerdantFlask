"""Users functional tests fixture file"""
import pytest
from werkzeug.security import generate_password_hash

from root.routes.users.models import User

USERNAME = "testuser"
EMAIL = "testuser@email.com"
PASSWORD = "testuserpass1"
PASSWORD_HASH = generate_password_hash(PASSWORD)


@pytest.fixture(scope="module")
def user(client_module):
    """Create a fresh user testing"""
    new_user = User(username=USERNAME, email=EMAIL, password_hash=PASSWORD_HASH,)
    new_user.save()
    assert new_user.username == USERNAME
    assert new_user.email == EMAIL
    assert new_user.password_hash == PASSWORD_HASH
    yield new_user
    new_user.delete()


@pytest.fixture()
def logged_in_user(client, user):
    """Log in the created user"""
    form_data = {"username_or_email": USERNAME, "password": PASSWORD}
    response = client.post("/users/login", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert f"Welcome {USERNAME}!" in response.data.decode()
    yield user
