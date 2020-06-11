"""Tests for root/utils methods"""
import os
import shutil

import pytest
from werkzeug.datastructures import FileStorage
from PIL import Image

from root.globals import PROJECT_ROOT_PATH
from root.image_handler import (
    delete_image,
    upload_image,
    prep_image,
    ALLOWED_EXTENSIONS,
)


TEST_IMAGES_PATH = os.path.join(PROJECT_ROOT_PATH, "test_data", "images")
IMAGE_STORAGE_PATH = os.path.join(TEST_IMAGES_PATH, "image_storage")
EXAMPLE_IMAGES_PATH = os.path.join(TEST_IMAGES_PATH, "example_images")


@pytest.fixture()
def example_images():
    """Prepare example images for testing"""
    example_images = []
    for image in os.listdir(EXAMPLE_IMAGES_PATH):
        fp = open(os.path.join(EXAMPLE_IMAGES_PATH, image), "rb")
        example_images.append(FileStorage(fp))
    yield example_images
    for image in example_images:
        image.close()


@pytest.fixture(autouse=True)
def prep_image_storage_path():
    """Create fresh image storage directory and delete afterwards"""
    shutil.rmtree(IMAGE_STORAGE_PATH, ignore_errors=True)
    os.mkdir(IMAGE_STORAGE_PATH)
    yield
    shutil.rmtree(IMAGE_STORAGE_PATH, ignore_errors=True)


def test_prep_image(example_images):
    """
    GIVEN an image and allowed extensions
    THEN return extension type and mod timestamp of allowed image

    prep_image(pic, allowed_extensions=ALLOWED_EXTENSIONS)
    """
    for image in example_images:
        ext_type_pre = image.filename.split(".")[-1]
        ext_type, mod_timestamp = prep_image(image)
        if ext_type_pre in ALLOWED_EXTENSIONS:
            assert ext_type == ext_type_pre
            assert mod_timestamp.isdigit() is True
        else:
            assert (ext_type, mod_timestamp) == (None, None)


def test_upload_image(example_images):
    """
    GIVEN an image, path, prefix, max_pixels and allowed extensions
    WHEN multiple image types and sizes are passed
    THEN all images should upload to filesystem

    upload_image(
        pic, path, prefix="", max_pixels=1_000, allowed_extensions=ALLOWED_EXTENSIONS
    )
    """
    success1 = []
    success2 = []
    success3 = []
    for image in example_images:
        ext_type_pre = image.filename.split(".")[-1]
        storage_filename1 = upload_image(image, IMAGE_STORAGE_PATH)
        storage_filename2 = upload_image(image, IMAGE_STORAGE_PATH, prefix="pre_")
        storage_filename3 = upload_image(image, IMAGE_STORAGE_PATH, prefix="small_", max_pixels=20)
        if ext_type_pre in ALLOWED_EXTENSIONS:
            assert isinstance(storage_filename1, str)
            assert isinstance(storage_filename2, str)
            assert isinstance(storage_filename3, str)
            success1.append(storage_filename1)
            success2.append(storage_filename2)
            success3.append(storage_filename3)
        else:
            assert storage_filename1 is None
            assert storage_filename2 is None
            assert storage_filename3 is None
    assert len(success1) == 2
    for filename in success1:
        assert os.path.isfile(os.path.join(IMAGE_STORAGE_PATH, filename))
    for filename in success2:
        assert os.path.isfile(os.path.join(IMAGE_STORAGE_PATH, filename))
        assert filename.startswith("pre_")
    for filename in success3:
        filepath = os.path.join(IMAGE_STORAGE_PATH, filename)
        assert os.path.isfile(filepath)
        assert filename.startswith("small_")
        image = Image.open(filepath)
        assert (image.width == 20 or image.height == 20)


def test_delete_image():
    """
    GIVEN an image relative path and absolute directory path
    THEN delete that image from the file system

    delete_image(rel_path, abs_path_dir)
    """
    for i, image_name in enumerate(os.listdir(EXAMPLE_IMAGES_PATH)):
        ext = image_name.split('.')[-1]
        new_filename = f"{i}.{ext}"
        get_path = os.path.join(EXAMPLE_IMAGES_PATH, image_name)
        put_path = os.path.join(IMAGE_STORAGE_PATH, new_filename)
        fake_relpath = os.path.join("fakepath", new_filename)
        image = Image.open(get_path)
        image.save(put_path)
        assert os.path.isfile(put_path)
        delete_image(fake_relpath, IMAGE_STORAGE_PATH)
        assert not os.path.isfile(put_path)
