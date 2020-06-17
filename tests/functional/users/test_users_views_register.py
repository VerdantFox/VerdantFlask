"""Test the user views"""
import pytest


def test_register_get(client):
    """Test the GET method on user register"""
    response = client.get("/users/register")
    assert response.status_code == 200
    data = response.data
    # href links present
    assert b'href="/users/login">Login</a>' in data
    assert b'href="/users/register">Register</a>' in data
    assert b'href="/users/facebook_oauth">' in data
    assert b'href="/users/google_oauth">' in data
    assert b'href="/users/github_oauth">' in data
    # form inputs present
    assert (
        b'<input class="form-control" id="email" name="email" '
        b'placeholder="Email" required type="text" value="">' in data
    )
    assert (
        b'<input class="form-control" id="username" name="username" '
        b'placeholder="Username" required type="text" value="">' in data
    )
    assert (
        b'<input class="form-control" id="password" name="password" '
        b'placeholder="Password" required type="password" value="">' in data
    )
    assert (
        b'<input class="form-control" id="pass_confirm" name="pass_confirm" '
        b'placeholder="Password confirm" required type="password" value="">' in data
    )
    assert (
        b'<input class="btn btn-lg btn-green" id="submit" name="submit" '
        b'type="submit" value="Register">' in data
    )


def test_register_post_happy(client, drop_db):
    """Test the POST method on user register when success expected"""
    username = "testuser"
    form_data = {
        "email": "testuser@gmail.com",
        "username": username,
        "password": "blah1234",
        "pass_confirm": "blah1234",
    }
    response = client.post("/users/register", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    data = response.data
    data_decoded = data.decode()
    # Flash messages
    assert f"Thanks for registering, {username}" in data_decoded
    assert (
        b"You can change your username and profile picture in the "
        b"<a href='/users/edit_profile' class='c-blue'>edit profile</a> page." in data
    )
    assert f"Welcome {username}!" in data_decoded
    # Top right icon
    assert f"Welcome, {username}" in data_decoded


BAD_FORMS = [
    pytest.param(
        {
            "email": "",
            "username": "testuser",
            "password": "blah1234",
            "pass_confirm": "blah1234",
        },
        b'<p class="error">This field is required.</p>',
        id="missing_email",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "",
            "password": "blah1234",
            "pass_confirm": "blah1234",
        },
        b'<p class="error">This field is required.</p>',
        id="missing_username",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "testuser",
            "password": "",
            "pass_confirm": "blah1234",
        },
        b'<p class="error">This field is required.</p>',
        id="missing_password",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "testuser",
            "password": "blah1234",
            "pass_confirm": "",
        },
        b'<p class="error">This field is required.</p>',
        id="missing_pw_confirm",
    ),
    pytest.param(
        {
            "email": "bademail",
            "username": "testuser",
            "password": "blah1234",
            "pass_confirm": "blah1234",
        },
        b"Invalid email address.",
        id="bad_email",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "a$21^",
            "password": "blah1234",
            "pass_confirm": "blah1234",
        },
        b'<p class="error">Must contain only letters, numbers, dashes and underscores.</p>',
        id="bad_username_chars",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "a",
            "password": "blah1234",
            "pass_confirm": "blah1234",
        },
        b'<p class="error">Field must be between 3 and 30 characters long.</p>',
        id="username_too_short",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "aasdfasdfasdfasdfasdfasdfasdfasd",
            "password": "blah1234",
            "pass_confirm": "blah1234",
        },
        b'<p class="error">Field must be between 3 and 30 characters long.</p>',
        id="username_too_long",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "testuser",
            "password": "b1",
            "pass_confirm": "b1",
        },
        b'<p class="error">Field must be between 8 and 30 characters long.</p>',
        id="password_too_short",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "testuser",
            "password": "assdf1234asdf1234asdfasdfasdfasdfasdfas",
            "pass_confirm": "assdf1234asdf1234asdfasdfasdfasdfasdfas",
        },
        b'<p class="error">Field must be between 8 and 30 characters long.</p>',
        id="password_too_long",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "testuser",
            "password": "pwwithoutnumbers",
            "pass_confirm": "pwwithoutnumbers",
        },
        b'<p class="error">At least one number required.</p>',
        id="password_no_nums",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "testuser",
            "password": "1234567890",
            "pass_confirm": "1234567890",
        },
        b'<p class="error">At least one letter required.</p>',
        id="password_no_letters",
    ),
    pytest.param(
        {
            "email": "test@email.com",
            "username": "testuser",
            "password": "goodpw123",
            "pass_confirm": "notmatching123",
        },
        b'<p class="error">Passwords Must Match!</p>',
        id="passwords_dont_match",
    ),
]


@pytest.mark.parametrize("form_data, expected", BAD_FORMS)
def test_register_post_fail(client, drop_db, form_data, expected):
    """Test the POST method on user register when success expected"""
    response = client.post("/users/register", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    data = response.data
    assert expected in data
