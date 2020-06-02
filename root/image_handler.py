import ntpath
import os
from datetime import datetime

from flask import flash
from flask_login import current_user
from PIL import Image
from werkzeug.utils import secure_filename

from root.externals import STATIC_PATH

AVATAR_UPLOAD_FOLDER = os.path.join(STATIC_PATH, "images", "avatars_uploaded")
BLOG_UPLOAD_FOLDER = os.path.join(STATIC_PATH, "images", "blog_uploaded")
for path in (AVATAR_UPLOAD_FOLDER, BLOG_UPLOAD_FOLDER):
    if not os.path.isdir(path):
        os.mkdir(path)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def prep_image(pic):
    """Common first steps to image uploading"""
    filename = pic.filename
    ext_type = filename.split(".")[-1].lower()
    mod_timestamp = str(datetime.now().timestamp()).replace(".", "")
    if ext_type not in ALLOWED_EXTENSIONS:
        flash(f"Invalid image extension type '{ext_type}'")
        return None, None
    return ext_type, mod_timestamp


def upload_image(pic, path, max_pixels=1_000):
    """Uploads a general image"""
    ext_type, mod_timestamp = prep_image(pic)
    if ext_type is None:
        return
    storage_filename = secure_filename(f"{mod_timestamp}.{ext_type}")
    filepath = os.path.join(path, storage_filename)
    pic = Image.open(pic)
    output_size = (max_pixels, max_pixels)
    pic.thumbnail(output_size)
    pic.save(filepath)

    return storage_filename


def upload_blog_image(pic):
    """Upload a blog image"""
    return upload_image(pic, BLOG_UPLOAD_FOLDER)


def upload_avatar(pic):
    """Uploads a user's avatar to static/images/avatars_uploaded"""
    ext_type, mod_timestamp = prep_image(pic)
    if ext_type is None:
        return
    storage_filename = secure_filename(f"{current_user.id}_{mod_timestamp}.{ext_type}")
    filepath = os.path.join(AVATAR_UPLOAD_FOLDER, storage_filename)
    delete_current_avatar()
    pic = Image.open(pic)
    output_size = (400, 400)
    pic.thumbnail(output_size)
    pic.save(filepath)

    return storage_filename


def delete_image(rel_path, abs_path_dir):
    """Delete image given a relative filepath"""
    # Want absolute file path
    filename = ntpath.basename(rel_path)
    filepath = os.path.join(abs_path_dir, filename)
    if os.path.exists(filepath):
        os.remove(filepath)


def delete_blog_image(rel_path):
    """Delete a blog image"""
    delete_image(rel_path, BLOG_UPLOAD_FOLDER)


def delete_current_avatar():
    """delete the current user's uploaded avatar if it exists"""
    av_loc = current_user.avatar_location
    if av_loc and "avatars_default" not in av_loc:
        delete_image(av_loc, AVATAR_UPLOAD_FOLDER)
