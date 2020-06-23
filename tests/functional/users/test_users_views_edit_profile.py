"""Test users edit profile view"""
import os
from datetime import date

import pytest
from werkzeug.datastructures import FileStorage

from root.globals import PROJECT_ROOT_PATH
from tests.conftest import bool_field_val
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


UPDATED_USERS = [
    pytest.param(
        {
            "username": "new_username",
            "full_name": "New Name",
            "share_name": bool_field_val(False),
            "upload_avatar": "REPLACE",
            "bio": "New bio!",
            "birth_date": date(2011, 3, 18),
            "share_birth_date": bool_field_val(False),
        },
        id="change_all",
    ),
    pytest.param(
        {
            "username": "second_username",
            "full_name": "Second Name",
            "share_name": bool_field_val(True),
            "select_avatar": "new_loc2.jpeg",
            "bio": "New bio 2!",
            "birth_date": date(2014, 1, 1),
            "share_birth_date": bool_field_val(True),
        },
        id="select_avatar",
    ),
    pytest.param(
        {
            "username": "third_username",
            "full_name": "",
            "share_name": bool_field_val(False),
            "bio": "",
            "birth_date": None,
            "share_birth_date": bool_field_val(False),
        },
        id="fields_removed",
    ),
]


@pytest.mark.parametrize("form_data", UPDATED_USERS)
def test_users_edit_profile_post_happy(
    client,
    logged_in_user1_mod,
    revert_user1,
    form_data,
    filesystem_image_jpg,
    tmpdir,
    mocker,
):
    """Test that editing a profile changes user values"""
    image_storage_path = tmpdir.mkdir("image_storage")
    mocker.patch("root.image_handler.AVATAR_UPLOAD_FOLDER", str(image_storage_path))
    if form_data.get("upload_avatar") == "REPLACE":
        form_data["upload_avatar"] = filesystem_image_jpg
    response = client.post("/users/edit_profile", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"User Profile Updated" in response.data
    response = client.get("/users/edit_profile")
    assert response.status_code == 200
    data = response.data.decode()
    assert (
        f'<input class="form-control text-center" id="username" name="username" '
        f'placeholder="Username" required type="text" value="{form_data["username"]}">'
        in data
    )
    assert (
        '<input class="form-control text-center" id="full_name" name="full_name" '
        f'placeholder="Your Name" type="text" value="{form_data["full_name"]}">' in data
    )
    assert (
        f'<input checked class="form-check-input" id="share_name" name="share_name" '
        f'placeholder="Share Name" type="checkbox" '
        f'value="{bool_field_val(form_data["share_name"])}">' in data
    )
    if form_data.get("upload_avatar"):
        assert (
            f'<img src="/static/images/avatars_uploaded/{logged_in_user1_mod.id}'
            in data
        )
    elif loc := form_data.get("select_avatar"):
        assert f'<img src="/static/images/avatars_default/{loc}' in data
    else:
        assert f'<img src="{logged_in_user1_mod.avatar_location}' in data
    assert f'{form_data["bio"]}</textarea>' in data
    birth_date = (
        date_str_fmt_forms(form_data["birth_date"]) if form_data["birth_date"] else ""
    )
    assert (
        f'<input class="form-control text-center" id="birth_date" name="birth_date" '
        f'placeholder="" type="date" value="{birth_date}">' in data
    )
    assert (
        '<input checked class="form-check-input" id="share_birth_date" '
        'name="share_birth_date" placeholder="Share Birthdate" type="checkbox" '
        f'value="{bool_field_val(form_data["share_birth_date"])}">' in data
    )


def test_users_edit_profile_post_bad_image_extension_fails(
    client, logged_in_user1_mod, revert_user1, filesystem_image_gif,
):
    """Test that a bad image extension fails with flash message"""
    form_data = {
        "username": "new_username",
        "full_name": "New Name",
        "share_name": bool_field_val(False),
        "upload_avatar": filesystem_image_gif,
        "bio": "New bio!",
        "birth_date": date(2011, 3, 18),
        "share_birth_date": bool_field_val(False),
    }
    response = client.post("/users/edit_profile", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "User Profile Updated" not in data
    assert "Invalid image extension type used!" in data
    assert (
        f'<input class="form-control text-center" id="username" name="username" '
        f'placeholder="Username" required type="text" value="{revert_user1.username}">'
        in data
    )


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
@pytest.fixture
def filesystem_image_jpg():
    """Yields jpg filesystem image for testing"""
    fp = open(get_image_path("test_jpeg.jpg"), "rb")
    yield FileStorage(fp)
    fp.close()


@pytest.fixture
def filesystem_image_gif():
    """Yields gif filesystem image for testing"""
    fp = open(get_image_path("test_gif.gif"), "rb")
    yield FileStorage(fp)
    fp.close()


def get_image_path(image):
    """Get filesystem image path"""
    return os.path.join(
        PROJECT_ROOT_PATH, "test_data", "images", "example_images", image
    )
