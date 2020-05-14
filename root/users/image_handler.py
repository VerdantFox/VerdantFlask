import ntpath
import os
from datetime import datetime

from flask import flash
from flask_login import current_user
from PIL import Image
from werkzeug.utils import secure_filename

from root.externals import STATIC_PATH

UPLOAD_FOLDER = os.path.join(STATIC_PATH, "images", "avatars_uploaded")
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def upload_avatar(pic):
    """Uploads a user's avatar to static/images/avatars_uploaded"""
    filename = pic.filename
    ext_type = filename.split(".")[-1].lower()
    mod_timestamp = str(datetime.now().timestamp()).replace(".", "")
    if ext_type not in ALLOWED_EXTENSIONS:
        flash(f"Invalid image extension type '{ext_type}'")
        return None
    storage_filename = secure_filename(f"{current_user.id}_{mod_timestamp}.{ext_type}")
    filepath = os.path.join(UPLOAD_FOLDER, storage_filename)
    output_size = (400, 400)
    print(f"filepath={filepath}")
    delete_current_avatar()
    pic = Image.open(pic)
    pic.thumbnail(output_size)
    pic.save(filepath)

    return storage_filename


def delete_current_avatar():
    """delete the current user's uploaded avatar if it exists"""
    av_loc = current_user.avatar_location
    if av_loc and "avatars_default" not in av_loc:
        # Want absolute file path
        filename = ntpath.basename(av_loc)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
