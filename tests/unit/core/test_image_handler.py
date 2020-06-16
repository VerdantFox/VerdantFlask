"""Tests for root/utils methods"""
import os

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from root.globals import PROJECT_ROOT_PATH
from root.image_handler import (
    ALLOWED_EXTENSIONS,
    delete_image,
    prep_image,
    upload_image,
)

TEST_IMAGES_PATH = os.path.join(PROJECT_ROOT_PATH, "test_data", "images")
# IMAGE_STORAGE_PATH = os.path.join(TEST_IMAGES_PATH, "image_storage")
EXAMPLE_IMAGES_DIR = os.path.join(TEST_IMAGES_PATH, "example_images")
EXAMPLE_IMAGE_PATHS = [
    os.path.join(EXAMPLE_IMAGES_DIR, image) for image in os.listdir(EXAMPLE_IMAGES_DIR)
]


@pytest.fixture(params=EXAMPLE_IMAGE_PATHS)
def example_image(request):
    """Prepare example images for testing"""
    fp = open(request.param, "rb")
    yield FileStorage(fp)
    fp.close()


@pytest.fixture(params=EXAMPLE_IMAGE_PATHS)
def example_image_path(request):
    """Prepare example images for testing"""
    fp = open(request.param, "rb")
    yield FileStorage(fp)
    fp.close()


def test_prep_image(example_image):
    """
    GIVEN an image and allowed extensions
    THEN return extension type and mod timestamp of allowed image

    prep_image(pic, allowed_extensions=ALLOWED_EXTENSIONS)
    """
    ext_type_pre = example_image.filename.split(".")[-1]
    ext_type, mod_timestamp = prep_image(example_image)
    if ext_type_pre in ALLOWED_EXTENSIONS:
        assert ext_type == ext_type_pre
        assert mod_timestamp.isdigit() is True
    else:
        assert (ext_type, mod_timestamp) == (None, None)


PARAMS = [(None, None), ("pre_", None), (None, 20), ("pre_", 20)]


@pytest.mark.parametrize("prefix, max_pixels", PARAMS)
def test_upload_image(example_image, tmpdir, prefix, max_pixels):
    """
    GIVEN an image, path, prefix, max_pixels and allowed extensions
    WHEN multiple image types and sizes are passed
    THEN all images should upload to filesystem

    upload_image(
        pic, path, prefix="", max_pixels=1_000, allowed_extensions=ALLOWED_EXTENSIONS
    )
    """
    image_storage_path = tmpdir.mkdir("image_storage")
    ext_type_pre = example_image.filename.split(".")[-1]
    if prefix and max_pixels:
        storage_filename = upload_image(
            example_image, image_storage_path, prefix=prefix, max_pixels=max_pixels
        )
    elif prefix:
        storage_filename = upload_image(
            example_image, image_storage_path, prefix=prefix
        )
    elif max_pixels:
        storage_filename = upload_image(
            example_image, image_storage_path, max_pixels=max_pixels
        )
    else:
        storage_filename = upload_image(example_image, image_storage_path)
    if ext_type_pre in ALLOWED_EXTENSIONS:
        assert isinstance(storage_filename, str)
        assert os.path.isfile(os.path.join(image_storage_path, storage_filename))
        if prefix:
            assert storage_filename.startswith(prefix)
        if max_pixels:
            filepath = os.path.join(image_storage_path, storage_filename)
            image = Image.open(filepath)
            assert image.width == 20 or image.height == 20
    else:
        assert storage_filename is None


@pytest.mark.parametrize("get_path", EXAMPLE_IMAGE_PATHS)
def test_delete_image(get_path, tmpdir):
    """
    GIVEN an image relative path and absolute directory path
    THEN delete that image from the file system

    delete_image(rel_path, abs_path_dir)
    """
    image_storage_path = tmpdir.mkdir("image_storage")
    ext = get_path.split(".")[-1]
    new_filename = f"my_pic.{ext}"
    put_path = os.path.join(image_storage_path, new_filename)
    fake_relpath = os.path.join("fakepath", new_filename)
    image = Image.open(get_path)
    image.save(put_path)
    assert os.path.isfile(put_path)
    delete_image(fake_relpath, image_storage_path)
    assert not os.path.isfile(put_path)
