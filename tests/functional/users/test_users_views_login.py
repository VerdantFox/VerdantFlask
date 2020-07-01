"""Test users login view"""
import pytest

from tests.functional.users.conftest import EMAIL, PASSWORD, USERNAME


def test_login_get(client):
    """Test the GET method for users login view"""
    response = client.get("/users/login")
    assert response.status_code == 200
    data = response.data
    # href links present
    assert b'href="/users/login">Login</a>' in data
    assert b'href="/users/register">Register</a>' in data
    assert b'href="/users/facebook_oauth">' in data
    assert b'href="/users/google_oauth">' in data
    assert b'href="/users/github_oauth">' in data
    # Form entries
    assert (
        b'<input class="form-control" id="username_or_email" '
        b'name="username_or_email" placeholder="Username or email" '
        b'required type="text" value="">' in data
    )
    assert (
        b'<input class="form-control" id="password" name="password" '
        b'placeholder="Password" required type="password" value="">' in data
    )
    # TODO need to add Forgot username or password section
    assert b'<a href="#">Forgot username or password?</a>' in data
    assert b'<p>Need to register? <a href="/users/register">click here</a></p>' in data


GOOD_LOGINS = [
    pytest.param(
        {"username_or_email": USERNAME, "password": PASSWORD}, id="username_login",
    ),
    pytest.param({"username_or_email": EMAIL, "password": PASSWORD}, id="email_login",),
]


@pytest.mark.parametrize("form_data", GOOD_LOGINS)
def test_login_post_happy(client, user1_mod, form_data):
    """Test the POST method on user register when success expected"""
    response = client.post("/users/login", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    # banner
    assert f"Welcome {USERNAME}!" in data
    # top right corner
    assert f"Welcome, {USERNAME}" in data


BAD_LOGINS = [
    pytest.param(
        {"username_or_email": USERNAME, "password": "incorrectpw"}, id="bad_combo",
    ),
    pytest.param({"username_or_email": "", "password": ""}, id="empty_email",),
]


@pytest.mark.parametrize("form_data", BAD_LOGINS)
def test_login_post_fail(client, user1_mod, form_data):
    """Test the POST method on user register when success expected"""
    response = client.post("/users/login", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert f"Welcome {USERNAME}!" not in data
    assert "(email or username)/password combination not found"


REDIRECTS = [
    pytest.param("%2F", ">Welcome to Verdant Fox!</h1>", id="index"),
    pytest.param("%2Fusers%2Flogin", ">Welcome to Verdant Fox!</h1>", id="login"),
    pytest.param("%2Fusers%2Flogin", ">Welcome to Verdant Fox!</h1>", id="register"),
    pytest.param("%2Fblog%2F", "Blog Posts by Date", id="blog"),
]


@pytest.mark.parametrize("redirect, expected", REDIRECTS)
def test_login_redirects(client, user1_mod, redirect, expected):
    """Test the POST method redirects to correct location"""
    form_data = {"username_or_email": USERNAME, "password": PASSWORD}
    response = client.post(
        f"/users/login?next={redirect}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    # banner
    assert f"Welcome {USERNAME}!" in data
    # top right corner
    assert f"Welcome, {USERNAME}" in data
    # page specific
    assert expected in data
