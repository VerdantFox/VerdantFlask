# Form Based Imports
import pytz
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FileField,
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

# User Based Imports
from src.custom_form_validators import (
    has_letter,
    has_number,
    safe_string,
    unique_or_current_user_field,
    unique_user_field,
)

timezone_list = [(timezone, timezone) for timezone in pytz.common_timezones]


class LoginForm(FlaskForm):
    username_or_email = StringField(
        "Username or email",
        description="Username or email",
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Password", description="Password", validators=[DataRequired()]
    )
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    email = StringField(
        "Email",
        description="Email",
        validators=[
            DataRequired(),
            Email(),
            unique_user_field("Email is already registered."),
        ],
    )
    username = StringField(
        "Username",
        description="Username",
        validators=[
            DataRequired(),
            unique_user_field("Username is already taken."),
            safe_string(),
            Length(min=3, max=30),
        ],
    )
    password = PasswordField(
        "Password",
        description="Password",
        validators=[DataRequired(), Length(min=8, max=30), has_letter(), has_number()],
    )
    pass_confirm = PasswordField(
        "Confirm password",
        description="Password confirm",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords Must Match!"),
        ],
    )
    submit = SubmitField("Register")


class UserSettingsForm(FlaskForm):
    email = StringField(
        "Email",
        description="Email",
        validators=[
            Optional(),
            Email(),
            Length(max=200),
            unique_or_current_user_field("Email is already registered."),
        ],
    )
    share_email = BooleanField("Share Email", description="Share Email", default=False)
    password = PasswordField(
        "New Password",
        description="New password",
        validators=[Optional(), Length(min=8, max=30), has_letter(), has_number()],
    )
    pass_confirm = PasswordField(
        "Confirm password",
        description="Confirm password",
        validators=[Optional(), EqualTo("password", message="Passwords Must Match!")],
    )
    timezone = SelectField("Timezone", choices=timezone_list, default="UTC")
    share_timezone = BooleanField(
        "Share Timezone", description="Share Timezone", default=False
    )
    submit = SubmitField("Update")


class UserProfileForm(FlaskForm):
    username = StringField(
        "Username",
        description="Username",
        validators=[
            DataRequired(),
            unique_or_current_user_field("Username already exists."),
            safe_string(),
            Length(min=3, max=30),
        ],
    )
    full_name = StringField(
        "Full Name",
        description="Your Name",
        validators=[Optional(), Length(max=60)],
    )
    share_name = BooleanField("Share Name", description="Share Name", default=False)
    upload_avatar = FileField(
        "Upload Your Own Avatar", description="Upload avatar", validators=[Optional()]
    )
    select_avatar = HiddenField("Select avatar", validators=[Optional()])
    bio = TextAreaField(
        "About Me",
        description="What's something intereting you'd like to share?",
        validators=[Optional(), Length(max=1000)],
    )
    birth_date = DateField("Birth date", validators=[Optional()])
    share_birth_date = BooleanField(
        "Share Birthdate", description="Share Birthdate", default=False
    )
    submit = SubmitField("Update")
