import json
import re

from flask_login import current_user
from wtforms import ValidationError

from root.routes.blog.models import BlogPost
from root.routes.users.models import User
from root.utils import get_slug


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


def has_upper(message=None):
    """Validates that the field has uppercase letter"""
    if not message:
        message = "Uppercase letter required."

    def validation(form, field):
        up = any(letter.isupper() for letter in field.data)
        if not up:
            raise ValidationError(message)

    return validation


def has_lower(message=None):
    """Validates that the field has lowercase letter"""
    if not message:
        message = "Lowercase letter required."

    def validation(form, field):
        low = any(letter.islower() for letter in field.data)
        if not low:
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


def matching_password(message=None):
    """Validates that a user's password field matches its password in database"""
    if not message:
        message = "Password doesn't match our records."

    def validation(form, field):
        if field.data and not current_user.check_password(field.data):
            raise ValidationError(message)

    return validation


def required_if(other_field_name, message=None):
    """Makes field required if anothe field is filled out"""

    def validation(form, field):
        nonlocal message

        other_field = form._fields.get(other_field_name)
        if not message:
            message = f"Required if '{other_field.label.text}' field is filled out"
        if other_field is None:
            raise ValidationError(f"No field named '{other_field_name}' in form")
        if bool(other_field.data) and not field.data:
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


def safe_string_json_parsed(message=None, maximum=None):
    """Validates that the field matches some safe requirements

    Requirements:
    - contains only letters and numbers
    """
    if not message:
        message = "Must contain only letters, numbers, dashes and underscores."

    def validation(form, field):
        in_string = field.data.lower()

        strings = json.loads(in_string)
        pattern = re.compile(r"^[a-z0-9_-]+$")
        for string in strings:
            match = pattern.match(string)
            if not match:
                raise ValidationError(message)
            if maximum and len(string) > maximum:
                raise ValidationError(f"Can't be longer than {maximum} characters.")

    return validation
