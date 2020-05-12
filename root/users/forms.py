# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

# User Based Imports
from root.custom_form_validators import (
    has_lower,
    has_upper,
    safe_string,
    unique_or_current_user_field,
    unique_user_field,
)


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
        description="Old password",
        validators=[DataRequired(), Length(min=8, max=30), has_lower(), has_upper()],
    )
    pass_confirm = PasswordField(
        "Confirm password",
        description="Password confirm",
        validators=[
            DataRequired(),
            EqualTo("pass_confirm", message="Passwords Must Match!"),
        ],
    )
    submit = SubmitField("Register")


class UpdateUserForm(FlaskForm):
    email = StringField(
        "Email",
        description="Email",
        validators=[
            DataRequired(),
            Email(),
            unique_or_current_user_field("Email is already registered."),
        ],
    )
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
    new_pass = PasswordField(
        "New Password",
        description="New password",
        validators=[Optional(), Length(min=8, max=30), has_lower(), has_upper()],
    )
    pass_confirm = PasswordField(
        "Confirm password",
        description="Confirm password",
        validators=[Optional(), EqualTo("new_pass", message="Passwords Must Match!")],
    )
    submit = SubmitField("Update")
