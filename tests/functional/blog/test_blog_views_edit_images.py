"""Test blog edit images view"""
import os

import pytest
from PIL import Image

from tests.conftest import EXAMPLE_IMAGE_PATHS


def test_blog_edit_images_get_not_logged_in_fails(client, delete_blogposts, bp1):
    """Test GET of blogpost edit images fails with login redirect"""
    response = client.get(f"/blog/edit_images/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Please log in to access this page." in data


def test_blog_edit_images_get_no_admin_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test GET of blogpost edit images fails with 401 for non-admin user"""
    response = client.get(f"/blog/edit_images/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 403
    data = response.data.decode()
    assert "Only admin can edit post." in data


def test_blog_edit_images_get_non_existant_post_fails(
    client, current_user_admin, delete_blogposts
):
    """Test GET of blogpost edit images fails with 404 if slug not found"""
    response = client.get(
        "/blog/edit_images/some-nonexistant-post", follow_redirects=True
    )
    assert response.status_code == 404
    data = response.data.decode()
    assert "Blog post not found!" in data


def test_blog_edit_images_get_admin_happy(
    client, current_user_admin, delete_blogposts, bp1
):
    """Test GET of the blog edit images route as admin user who owns post succeeds"""
    response = client.get(f"/blog/edit_images/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "<h1>Edit Blog Post Images</h1>" in data
    assert "No Uploaded Images Found" in data


def test_blog_edit_images_submit_upload_happy(
    tmpdir, mocker, client, current_user_admin, delete_blogposts, bp1, example_image,
):
    """Test POST of blog image with happy upload form"""
    image_storage_path = tmpdir.mkdir("image_storage_tmp")
    mocker.patch("root.image_handler.BLOG_UPLOAD_FOLDER", image_storage_path)

    form_data = {
        "upload_image": example_image,
    }
    response = client.post(
        f"/blog/edit_images/{bp1.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "No Uploaded Images Found" not in data
    assert data.count("![image_name](/static/images/blog_uploaded/") == 1


@pytest.mark.parametrize("get_path", EXAMPLE_IMAGE_PATHS)
def test_blog_edit_images_submit_delete_happy(
    tmpdir, mocker, client, current_user_admin, delete_blogposts, bp1, get_path,
):
    """Test POST of blog image with happy delete form"""
    image_storage_path = tmpdir.mkdir("image_storage")
    ext = get_path.split(".")[-1]
    new_filename = f"my_pic.{ext}"
    put_path = os.path.join(image_storage_path, new_filename)
    image = Image.open(get_path)
    image.save(put_path)
    assert os.path.isfile(put_path)
    mocker.patch("root.image_handler.BLOG_UPLOAD_FOLDER", image_storage_path)
    form_data = {
        "delete_image": new_filename,
    }
    response = client.post(
        f"/blog/edit_images/{bp1.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "No Uploaded Images Found" in data
    assert data.count("![image_name](/static/images/blog_uploaded/") == 0
    assert not os.path.isfile(put_path)


def test_blog_edit_images_submit_delete_bad_type(
    tmpdir, mocker, client, current_user_admin, delete_blogposts, bp1, bad_image_type,
):
    """Test POST of blog image with bad type"""
    image_storage_path = tmpdir.mkdir("image_storage_tmp")
    mocker.patch("root.image_handler.BLOG_UPLOAD_FOLDER", image_storage_path)

    form_data = {
        "upload_image": bad_image_type,
    }
    response = client.post(
        f"/blog/edit_images/{bp1.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Invalid image extension type used!" in data
