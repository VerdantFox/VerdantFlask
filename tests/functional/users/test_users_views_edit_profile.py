"""Test users edit profile view"""
from tests.functional.users.conftest import date_str_fmt_forms


def test_users_edit_profile_get(client, logged_in_user1_mod, revert_user1):
    """Test the GET method for users edit profile view"""
    response = client.get("/users/edit_profile")
    assert response.status_code == 200
    data = response.data.decode()
    assert "<h1>Edit Profile</h1>" in data
    # Form entries
    assert (
        f'<input class="form-control text-center" id="username" name="username" '
        f'placeholder="Username" required type="text" value="{revert_user1.username}">'
        in data
    )
    assert (
        f'<input class="form-control text-center" id="full_name" name="full_name" '
        f'placeholder="Your Name" type="text" value="{revert_user1.full_name}">' in data
    )
    assert (
        f'<input checked class="form-check-input" id="share_name" name="share_name" '
        f'placeholder="Share Name" type="checkbox" value="{bool_field_val(revert_user1.share_name)}">'
        in data
    )
    assert f'<img src="{revert_user1.avatar_location}"' in data
    assert (
        '<input id="select_avatar" name="select_avatar" type="hidden" value="">' in data
    )

    assert (
        '<input class="custom-file-input" id="upload_avatar" '
        'name="upload_avatar" type="file">' in data
    )
    assert f"{revert_user1.bio}</textarea>" in data
    assert (
        f'<input class="form-control text-center" id="birth_date" name="birth_date" '
        f'placeholder="" type="date" value="{date_str_fmt_forms(revert_user1.birth_date)}">'
        in data
    )
    assert (
        f'<input checked class="form-check-input" id="share_birth_date" '
        f'name="share_birth_date" placeholder="Share Birthdate" type="checkbox" '
        f'value="{bool_field_val(revert_user1.share_birth_date)}">' in data
    )
    assert (
        '<input class="btn btn-lg btn-green" id="submit" name="submit" '
        'type="submit" value="Update">' in data
    )


def bool_field_val(boolean):
    """Convert a boolean to its html value equivalent"""
    return "y" if bool(boolean) else "n"
