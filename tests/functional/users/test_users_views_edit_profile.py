"""Test users edit profile view"""
import datetime
import os

import pytest
from werkzeug.datastructures import FileStorage

from root.globals import PROJECT_ROOT_PATH
from root.routes.users.models import User
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
        '<input checked class="form-check-input" id="share_name" name="share_name" '
        'placeholder="Share Name" type="checkbox" value="y">' in data
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
        '<input checked class="form-check-input" id="share_birth_date" '
        'name="share_birth_date" placeholder="Share Birthdate" type="checkbox" '
        'value="y">' in data
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
            "share_name": False,
            "upload_avatar": "REPLACE",
            "bio": "New bio!",
            "birth_date": datetime.date(2011, 3, 18),
            "share_birth_date": False,
        },
        id="change_all",
    ),
    pytest.param(
        {
            "username": "second_username",
            "full_name": "Second Name",
            "share_name": True,
            "select_avatar": "new_loc2.jpeg",
            "bio": "New bio 2!",
            "birth_date": datetime.date(2014, 1, 1),
            "share_birth_date": True,
        },
        id="select_avatar",
    ),
    pytest.param(
        {
            "username": "third_username",
            "full_name": "",
            "share_name": False,
            "bio": "",
            "birth_date": None,
            "share_birth_date": False,
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
    # Prepare the form
    image_storage_path = tmpdir.mkdir("image_storage")
    mocker.patch("root.image_handler.AVATAR_UPLOAD_FOLDER", str(image_storage_path))
    if form_data.get("upload_avatar") == "REPLACE":
        form_data["upload_avatar"] = filesystem_image_jpg
    form_copy = dict(form_data)
    for key, val in form_copy.items():
        if val is False:
            form_data.pop(key)

    # Submit the form
    response = client.post("/users/edit_profile", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"User Profile Updated" in response.data

    # Check changes took place
    user = User.objects(id=revert_user1.id).first()
    for key, val in form_copy.items():
        if key == "select_avatar":
            val = f"/static/images/avatars_default/{form_data[key]}"
            key = "avatar_location"
        elif key == "upload_avatar":
            val = f"/static/images/avatars_uploaded/{logged_in_user1_mod.id}"
            assert val in user.avatar_location
            continue
        elif key == "birth_date" and val is not None:
            val = datetime.datetime.combine(val, datetime.datetime.min.time())
        if val == "":
            val = None
        assert user[key] == val


def test_users_edit_profile_post_bad_image_extension_fails(
    client, logged_in_user1_mod, revert_user1, filesystem_image_gif,
):
    """Test that a bad image extension fails with flash message"""
    form_data = {
        "username": "new_username",
        "full_name": "New Name",
        "share_name": True,
        "upload_avatar": filesystem_image_gif,
        "bio": "New bio!",
        "birth_date": datetime.date(2011, 3, 18),
        "share_birth_date": True,
    }
    response = client.post("/users/edit_profile", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "User Profile Updated" not in data
    assert "Invalid image extension type used!" in data
    user = User.objects(id=revert_user1.id).first()
    assert user.username != form_data["username"]
    assert user.username == revert_user1.username


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
