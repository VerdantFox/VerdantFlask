"""Test the user views"""


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
    """Test the GET method on user register"""
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
    data_decoded = data.decode("utf-8")
    # Flash messages
    assert f"Thanks for registering, {username}" in data_decoded
    assert (
        b"You can change your username and profile picture in the "
        b"<a href='/users/edit_profile' class='c-blue'>edit profile</a> page." in data
    )
    assert f"Welcome {username}!" in data_decoded
    # Top right icon
    assert f"Welcome, {username}" in data_decoded
