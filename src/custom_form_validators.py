import re

from flask_login import current_user
from wtforms import ValidationError

from src.routes.blog.models import BlogPost
from src.routes.users.models import User
from src.utils import get_slug


def unique_blog_title(message=None):
    """Validates that a blog title doesn't already exist"""
    if not message:
        message = "Title must be unique"

    def validation(form, field):
        title = field.data
        slug = get_slug(title)
        if BlogPost.objects(slug=slug).first():
            raise ValidationError(message)

    return validation


def unique_user_field(message=None):
    """Validates that a field doesn't already exist in the database"""

    def validation(form, field):
        kwargs = {field.name: field.data}
        if User.objects(**kwargs).first():
            raise ValidationError(message)

    return validation


def unique_or_current_user_field(message=None):
    """Validates that a field is either equal to user's current field or doesn't exist"""

    def validation(form, field):
        kwargs = {field.name: field.data}
        if getattr(current_user, field.name) == field.data:
            return
        if User.objects(**kwargs).first():
            raise ValidationError(message)

    return validation


def has_letter(message=None):
    """Validates that the field has at least one letter"""
    if not message:
        message = "At least one letter required."

    def validation(form, field):
        lowercase_string = field.data.lower()
        contains_letters = lowercase_string.islower()
        if contains_letters is False:
            raise ValidationError(message)

    return validation


def has_number(message=None):
    """Validates that the field has at least one letter"""
    if not message:
        message = "At least one number required."

    def validation(form, field):
        contains_numbers = any(char.isdigit() for char in field.data)
        if not contains_numbers:
            raise ValidationError(message)

    return validation


def safe_string(message=None):
    """Validates that the field matches some safe requirements

    Requirements:
    - contains only letters and numbers
    """
    if not message:
        message = "Must contain only letters, numbers, dashes and underscores."

    def validation(form, field):
        string = field.data.lower()
        pattern = re.compile(r"^[a-z0-9_-]+$")
        match = pattern.match(string)
        if not match:
            raise ValidationError(message)

    return validation
