import ntpath
import os
from datetime import datetime
from typing import Iterable, Optional, Tuple

from flask_login import current_user
from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.globals import STATIC_PATH

AVATAR_UPLOAD_FOLDER = os.path.join(STATIC_PATH, "images", "avatars_uploaded")
BLOG_UPLOAD_FOLDER = os.path.join(STATIC_PATH, "images", "blog_uploaded")
for path in (AVATAR_UPLOAD_FOLDER, BLOG_UPLOAD_FOLDER):
    if not os.path.isdir(path):
        os.mkdir(path)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def prep_image(
    pic: FileStorage, allowed_extensions: Iterable[str] = ALLOWED_EXTENSIONS
) -> Tuple[Optional[str], Optional[str]]:
    """Common first steps to image uploading"""
    filename = str(pic.filename)
    ext_type = filename.split(".")[-1].lower()
    mod_timestamp = str(datetime.now().timestamp()).replace(".", "")
    if ext_type not in allowed_extensions:
        return None, None
    return ext_type, mod_timestamp


def upload_image(
    pic: FileStorage,
    path: str,
    prefix: str = "",
    max_pixels: int = 1_000,
    allowed_extensions: Iterable[str] = ALLOWED_EXTENSIONS,
) -> Optional[str]:
    """Uploads a general image"""
    ext_type, mod_timestamp = prep_image(pic, allowed_extensions)
    if ext_type is None:
        return None
    storage_filename = secure_filename(f"{prefix}{mod_timestamp}.{ext_type}")
    filepath = os.path.join(path, storage_filename)

    # Some bug with gifs in pillow causes messed up colors
    # So don't use pillow to resize
    if ext_type != "gif":
        pic = Image.open(pic)
        output_size = (max_pixels, max_pixels)
        pic.thumbnail(output_size)
    pic.save(filepath)
    pic.close()

    return storage_filename


def upload_blog_image(pic: FileStorage) -> Optional[str]:
    """Upload a blog image"""
    allowed_extensions = ALLOWED_EXTENSIONS.copy()
    allowed_extensions.add("gif")
    return upload_image(pic, BLOG_UPLOAD_FOLDER, allowed_extensions=allowed_extensions)


def upload_avatar(pic: FileStorage) -> Optional[str]:
    """Uploads a user's avatar to static/images/avatars_uploaded"""
    storage_filename = upload_image(
        pic, AVATAR_UPLOAD_FOLDER, prefix=f"{current_user.id}_", max_pixels=400
    )
    if storage_filename is not None:
        delete_current_avatar()
    return storage_filename


def delete_image(rel_path: str, abs_path_dir: str) -> None:
    """Delete image given a relative filepath and absolute directory"""
    # Want absolute file path
    filename = ntpath.basename(rel_path)
    filepath = os.path.join(abs_path_dir, filename)
    if os.path.exists(filepath):
        os.remove(filepath)


def delete_blog_image(rel_path: str) -> None:
    """Delete a blog image"""
    delete_image(rel_path, BLOG_UPLOAD_FOLDER)


def delete_current_avatar() -> None:
    """delete the current user's uploaded avatar if it exists"""
    av_loc = current_user.avatar_location
    if av_loc and "avatars_default" not in av_loc:
        delete_image(av_loc, AVATAR_UPLOAD_FOLDER)
