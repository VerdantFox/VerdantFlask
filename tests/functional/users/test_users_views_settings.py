"""Test users edit profile view"""
import pytest

from root.routes.users.models import User


def test_users_account_settings_get(client, logged_in_user1_mod, revert_user1):
    """Test the GET method for users account settings view"""
    response = client.get("/users/account_settings")
    assert response.status_code == 200
    data = response.data.decode()
    assert "<h1>Account Settings</h1>" in data
    assert (
        '<input class="form-control" id="email" name="email" placeholder="Email" '
        f'type="text" value="{revert_user1.email}">' in data
    )
    assert (
        '<input checked class="form-check-input" id="share_email" name="share_email" '
        'placeholder="Share Email" type="checkbox" value="y">' in data
    )
    assert (
        '<input class="form-control" id="password" name="password" '
        'placeholder="New password" type="password" value="">' in data
    )
    assert (
        '<input class="form-control" id="pass_confirm" name="pass_confirm" '
        'placeholder="Confirm password" type="password" value="">' in data
    )
    assert (
        f'<option selected value="{revert_user1.timezone}">{revert_user1.timezone}</option>'
        in data
    )
    assert (
        '<input checked class="form-check-input" id="share_timezone" '
        'name="share_timezone" placeholder="Share Timezone" type="checkbox" '
        'value="y">' in data
    )
    assert (
        '<input class="btn btn-lg btn-green" id="submit" '
        'name="submit" type="submit" value="Update">' in data
    )
    assert '<h5><a href="/users/facebook_oauth">Connect to Facebook</a></h5>' in data
    assert '<h5><a href="/users/google_oauth">Connect to Google</a></h5>' in data
    assert '<h5><a href="/users/github_oauth">Connect to GitHub</a></h5>' in data
    assert '<form method="post" action="/users/delete_account">' in data


UPDATES_SET1 = [
    pytest.param(
        {
            "email": "new@yahoo.com",
            "share_email": False,
            "password": "mynewpass12345",
            "pass_confirm": "mynewpass12345",
            "timezone": "Pacific/Tahiti",
            "share_timezone": False,
        },
        id="change_all",
    ),
    pytest.param(
        {
            "email": "",
            "share_email": True,
            "password": "",
            "pass_confirm": "",
            "timezone": "UTC",
            "share_timezone": True,
        },
        id="minimal",
    ),
]


@pytest.mark.parametrize("form_data", UPDATES_SET1)
def test_users_account_settings_post_happy(
    client, logged_in_user1_mod, revert_user1, form_data,
):
    """Test that editing a profile changes user values"""
    form_copy = dict(form_data)
    for key, val in form_copy.items():
        if val is False:
            form_data.pop(key)
    response = client.post(
        "/users/account_settings", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "User Account Updated" in data
    user = User.objects(id=revert_user1.id).first()
    for key, val in form_copy.items():
        if key == "pass_confirm":
            continue
        if key == "password":
            if val == "":
                assert user.password_hash == revert_user1.password_hash
            else:
                assert user.check_password(val)
            continue
        if key == "email" and val == "":
            assert user.email == revert_user1.email
            continue
        assert user[key] == val
