from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash

from root.users.models import User
from root.users.forms import RegistrationForm, LoginForm, UpdateUserForm


users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    """Registers the user in 'flask' database, 'users' collection"""
    logout_user()
    form = RegistrationForm()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=password_hash,
        )
        user.save()
        flash("Thanks for registering! Now you can login!", category="success")
        return redirect(url_for("users.login"))
    return render_template("users/register.html", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    """Logs the user in"""
    logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        username_or_email = form.username_or_email.data
        if "@" in username_or_email:
            user = User.objects(email=username_or_email).first()
        else:
            user = User.objects(username=username_or_email).first()

        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash("You have logged in.", category="success")

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get("next")

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next is None or not next[0] == "/":
                next = url_for("core.index")

            return redirect(next)
        else:
            flash(
                "(email or username)/password combination not found", category="error"
            )

    return render_template("users/login.html", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "success")
    return redirect(url_for("users.login"))


@users.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return "PROFILE"


@users.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    return "EDIT profile"


@users.route("/account_settings", methods=["GET", "POST"])
@login_required
def account_settings():

    form = UpdateUserForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        fields = {
            "email": form.email.data,
            "username": form.username.data,
        }
        if form.new_pass.data:
            new_hash = generate_password_hash(form.new_pass.data)
            fields["password_hash"] = new_hash
        current_user.update(**fields)
        flash("User Account Updated", category="success")
        return redirect(url_for("users.account"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("users/account_settings.html", form=form)
